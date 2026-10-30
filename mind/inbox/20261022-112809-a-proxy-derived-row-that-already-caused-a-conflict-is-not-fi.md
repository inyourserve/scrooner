---
id: a-proxy-derived-row-that-already-caused-a-conflict-is-not-fi
title: A proxy-derived row that already caused a conflict is not fixed by gating derivation inputs
kind: lesson
tags: derivation, per-share, periodic-form, jpm
paths: pipeline/src/scrooner_pipeline/normalizer/derived.py, pipeline/src/scrooner_pipeline/common/derivation_policy.py
evidence: DATA-INFERRED
source: data-team/22-FILING-LESSONS-LEDGER.md 2026-10-22 JPM row
created: 2026-10-22
verified: 2026-10-22
---
derived.py now takes only 10-K/10-Q-family inputs (common/derivation_policy.PERIODIC_FORMS_DOMESTIC). Old rows derived from DEF 14A/8-K FY values remain: JPM Q4 2025 proxy-derived 12,977M (core.fact 182608846) and 10-K-derived 13,025M (340478) are both non-authoritative after Stage 2e, so net_income falls to the derived to-common tag (12,691M). Fix needs conflict grouping to ignore non-periodic derived rows, not a demotion.
