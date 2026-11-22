---
id: dimensioned-resolver-parts-core-fact-has-no-dimension-column
title: Dimensioned resolver parts: core.fact has no dimension column, fsn.value x fsn.dim is the only store
kind: lesson
tags: member, dimension, structural-direct, fsn
paths: pipeline/src/scrooner_pipeline/common/member_facts.py
evidence: DATA-INFERRED
status: active
created: 2026-11-14
verified: 2026-11-14
---
Resolver Tag[Member] parts (axis not printed) and member_face_fact rows resolve to ONE fsn.value with a single-segment fsn.dim in the claim's own accession and column. Same member under two axes (ACN CommonClassX: ClassOfStock and EquityComponents) is ambiguous unless the resolver rule flag names the axis (class_sum, ap/ar_related_sum, cor_member_sum). TMUS: resolver prints member Product, the store holds ProductEquipment (same value) so exact match rejects. Query fsn.value by filing_id, never by company+tag with dim_id<>0 (times out).
