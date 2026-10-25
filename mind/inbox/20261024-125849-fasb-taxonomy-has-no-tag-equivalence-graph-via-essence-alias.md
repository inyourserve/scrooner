---
id: fasb-taxonomy-has-no-tag-equivalence-graph-via-essence-alias
title: FASB taxonomy has no tag-equivalence graph via essence-alias/general-special; use calc tree, meta-model and dep arcs
kind: reference
tags: taxonomy, essence-alias, calc linkbase, deprecation, FSDS, FSN
paths: data-team/tags/sources.md, data-team/strategy/team/OPEN-SOURCES-FOR-COVERAGE-2026-10-24.md
evidence: DOC-CITED
source: xbrl.fasb.org us-gaap-2026.zip, read 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
2026 taxonomy: essence-alias 22 arcs (all in us-gaap-depcon-def, deprecated items only), general-special 0. Useful: summation-item 6,633, class-subclass 1,573, concept-dimensional-equivalent 301, aggregate-other 163, dep-* 405 (replacement per deprecated element; yearly depcon-def files, e.g. 2023/2024 EarningsPerShareBasicAndDiluted -> Basic + Diluted). Sizes: taxonomy zip 7.4 MB/yr; FSDS 60-85 MB/qtr (num has a segments column = dimensional face facts companyfacts strips); FSN monthly 41-314 MB (2025_11 292 MB, 2.0 GB unpacked; note facts added ~nothing to the residue test, cal.tsv is the useful part); companyfacts.zip 1.41 GB/day.
