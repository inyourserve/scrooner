---
id: fsds-num-txt-ddate-is-month-rounded-values-have-4-decimals-p
title: FSDS num.txt: ddate is month-rounded, values have 4 decimals, per-share uom is USD
kind: gotcha
tags: fsds, as-filed, dates
paths: data-team/strategy/team/AS-FILED-PILOT-2026-10-24.md
evidence: FILING-CHECKED
source: data engineer as-filed pilot 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
FSDS ddate rounds to the nearest month-end (AAPL 2020-03-28 reads 2020-03-31, MU 2021-09-02 reads 2021-08-31), no start date (only qtrs), values truncated to 4 decimals (par 0.00001 reads 0.0000; 185 cells), per-share facts have uom USD. Apply the same rounding to our dates before matching or 52/53-week filers (MU, AVGO) show thousands of false absent facts. Exact dates and tiny values need the instance.
