---
id: parsers-calculators-are-registries-not-one-file--763145
title: Parsers/calculators are registries, not one-file-per-concept sprawl
kind: gotcha
tags: pipeline
paths: pipeline/CLAUDE.md
evidence: DOC-CITED
source: pipeline/CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
: `parsers/main_parser.py`'s `PARSER_REGISTRY` (concept → dedicated rendered-report parser, e.g. `revenue_parser.py`, `cost_of_revenue_parser.py`), backed by `analytics.concept_parser_result`/`concept_parser_attempt` (kept separate from `canonical_fact`, which stays `resolve()`'s exclusive output). `mapper/main_calculator.py`'s `METRIC_CALCULATOR_REGISTRY` maps every metric to whichever of `calculate.py`'s generic engine or a specialized module computes it. `calculate.py`'s own internal formula-shape dispatch is further split into `calculate_shapes/` (one file per shape: ratio/sum_diff/sum_diff_ratio/additive/days/roic). New shapes/parsers/calculators are added only once a real, *sized* gap justifies it — never preemptively.
