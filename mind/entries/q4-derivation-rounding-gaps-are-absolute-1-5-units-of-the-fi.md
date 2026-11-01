---
id: q4-derivation-rounding-gaps-are-absolute-1-5-units-of-the-fi
title: Q4 derivation: rounding gaps are absolute (1.5 units of the filer's presentation scale), a scale-free tolerance misclassifies them as vintage mismatches
kind: lesson
tags: q4, derivation, vintage, rounding, tolerance, period-engineer
paths: pipeline/src/scrooner_pipeline/normalizer/q4_vintage_dryrun.py
evidence: FILING-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/src/scrooner_pipeline/normalizer/q4_vintage_hold.py
---
Checked 10 NVDA/AAPL/AMD cells the same-vintage hold flagged with a 0.05% relative tolerance: all 10 were rounding, 0 recasts. Two shapes: (1) 9M YTD vs Q1+Q2+Q3 differ by 1M when the filer reports in millions (sum of three rounded numbers; NVDA 327 vs 326); (2) presentation switch thousands -> millions across 10-Ks (NVDA FY2015 net income 630,587,000 then 631,000,000). Relative sizes 0.3% to 4.8%, while PM's real recast (3,412 vs 3,429 opex) is 0.5%: no relative threshold separates them. Working rule: abs slack = 1.5 x 10^(median trailing-zero exponent of the company's authoritative FY USD facts, capped at 6). Residual false holds after that: lines a filer rounds coarser than its own scale (AAPL interest expense, GOOG SBC to the nearest 100M) and intra-year inconsistencies where Q1+Q2+Q3 differ from the 9M by 2 units (NVDA operating income 2016: 176+76+245 = 497 vs 495), which are not vintage issues and deserve their own reason code. Real recasts look like AAPL FY2016 CFO 65,824 (FY2017 10-K) vs 66,231 (FY2018 10-K).
