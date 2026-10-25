---
id: yfinance-sanity-check-data-sanity-check-has-no-history-basel
title: yfinance sanity check: data_sanity_check has no history; baseline is counts only; NULL TTM snapshot is read as the older value
kind: gotcha
tags: sanity, yfinance
evidence: DATA-INFERRED
source: data-team/strategy/team/SANITY-REGRESSION-0927-2026-10-24.md
created: 2026-10-24
verified: 2026-10-24
---
analytics.data_sanity_check keeps one overwritten row per (company, metric) and data_sanity_gate_baseline keeps counts only, so a per-company 'what moved since the baseline' cannot be built. TTM metric_value rows keep daily snapshots (trailing_pe keeps one row), which allows a proxy. yfinance_check reads 'value is not null' while the product (resolve.py, getLatestMetrics) takes the newest snapshot including NULL: after the 150-day TTM guard (5eeb7a0) the check compares yfinance with an older snapshot the product hides (ebitda_margin 296 of 850 majors). Coverage growth also raises the major COUNT while the rate among evaluated rows falls (quick_ratio 24.5% to 21.8% after f67a927). f67a927 treats missing inventory as zero, which makes quick_ratio = current_ratio for inventory holders (NKE, BA, GAP, AZO, XOM filing-checked). Yahoo quickRatio = (cash+STI+AR)/current liabilities.
