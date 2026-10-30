---
id: pinnacle-company-4938-shows-synovus-s-statements-an-8-k-with
title: Pinnacle (company 4938) shows Synovus's statements: an 8-K with 769 facts won the latest-filed conflict fill over the 10-K; root fix is rule source.periodic_form_only@1 (W3), not a point demotion
kind: gotcha
tags: 8-K, authority, conflict_fill, W3, pinnacle, top1000
paths: pipeline/src/scrooner_pipeline/normalizer/conflict_latest_filed.py, pipeline/src/scrooner_pipeline/normalizer/dedupe.py, pipeline/scripts/w3_population_dryrun.py
evidence: FILING-CHECKED
source: data-team/strategy/team/VERIFY-RETIREMENT-B14-2026-10-26.md; W3 dry-run 2026-10-30 (scrooner-0f)
created: 2026-10-30
verified: 2026-10-30
---
Pinnacle's holdco 8-K 0002082866-26-000020 (Item 8.01/9.01, filed 2026-03-02, same day as its 10-K 0002082866-26-000018) carries Synovus Financial's full statements: 769 facts under company_id 4938, 410 authoritative. All 15 keys it shares with the 10-K disagree; 350 of its 359 non-authoritative facts sit in conflict groups where the 10-K copy is ALSO non-authoritative (Stage 2e demoted both). Stage 2e-b 'latest filing wins' (8-K is in FY_ELIGIBLE_FORMS; same filing date, tie by fact id) promoted the 8-K copies, so production shows FY2025 net income 791,980K (Synovus) instead of the 10-K's 641,865K, FY2024 482,460K instead of 475,056K. Lesson: a conflict-fill rule that lets 8-K copies win cannot tell a recast of the registrant's own statements from another entity's statements; only the periodic-form rule can. Branch work/data-engineer/lane1-identity-fixes-v2 commits a60a44c + 4bf20f1 implement W3 (dedupe ignores non-periodic filings, 2e-b bans 8-K/8-K/A/6-K winners, repair list purges canonical cells sourced from non-periodic filings); they cherry-pick cleanly onto origin/main (c5b6997), 52 unit tests pass. Pinnacle-only dry-run: 318 conflict groups clear to the 10-K copy, 15 authoritative values change (NetIncomeLoss, CFO/CFI/CFF, tax; all 8-K to 10-K), 432 groups go to no authoritative copy (395 8-K singletons, 37 DEF 14A), 76 stored canonical cells need the purge (70 sourced from the 8-K). Flag OFF everywhere; nothing applied.
