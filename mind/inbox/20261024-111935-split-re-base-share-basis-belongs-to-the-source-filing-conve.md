---
id: split-re-base-share-basis-belongs-to-the-source-filing-conve
title: Split re-base: share basis belongs to the SOURCE FILING; convert every copy by its filing's factor, show the latest when they agree
kind: lesson
tags: split, per-share, eps, shares, period
paths: pipeline/src/scrooner_pipeline/corporate_actions/share_basis.py
evidence: FILING-CHECKED
source: branch work/period-engineer/split-rebase e312dfb; AAPL 0000320193-20-000096 R2/R4; GOOG 0001652044-22-000071 R4; TSLA 0001564590-15-003789 R4
created: 2026-10-24
verified: 2026-10-24
---
factor(F) = product of confirmed split ratios whose basis_date (first filing observed on the new basis) > F.filing_date. AAPL FY2018 diluted 11.91 (FY2018 10-K) is re-presented 2.98 in the FY2020 10-K R2; GOOG Q2 2022 diluted 1.21 is already post-split in the 10-Q filed 2022-07-27 (period-end test divided it to 0.0605); TSLA Q1 2015 -1.22 was never re-presented so factor = 5x3 = 15. Event identity = (ratio, observed boundary) from filed pairs + share-count steps + ratio facts on instant AND duration contexts; confirmed needs 2 kinds. Gotchas found in the 11-company dry-run: exact 1000x between share copies is a units error (AAPL 10-Q 0001193125-14-157311 899,213 vs 899,213,000), not a reverse split; a 'product of two clean ratios' test matches almost any restatement, so the company invariant must require the same ratio on >=2 periods between one filing pair and ratios built only from the company's own events; re-presented DPS can be a sum of rounded quarters (AAPL FY2013 1.64 vs 11.40/7=1.6286), so cross-basis copies need ~2 cents slack; a Q4 DPS equal to the FY value is a label error only when the 9M YTD is positive (NVDA FY2015 yes, NVDA FY2013 first dividend no). Derived Q4 per-share cells keep wrong bases until RU-1 removes them (GOOG Q4 2016 0.01895): ship split.event_basis@1 with pershare.never_derive@1.
