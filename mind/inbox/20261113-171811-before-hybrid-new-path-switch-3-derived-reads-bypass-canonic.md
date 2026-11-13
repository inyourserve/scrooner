---
id: before-hybrid-new-path-switch-3-derived-reads-bypass-canonic
title: Before HYBRID_NEW_PATH switch: 3 derived reads bypass canonical_fact; refresh worst case 233 min vs 180 limit
kind: gotcha
evidence: CODE-CHECKED
created: 2026-11-13
verified: 2026-11-13
---
FSN nightly session 2026-11-13 (stopped; uncommitted fix on work/fsn-flag-prereqs, no test): quick_ratio inventory evidence reads analytics.concept_mapping (mapper/quick_ratio_evidence.py load_inventory_concept_ids); market cap reads diluted weighted shares from core.fact (price_metrics._load_latest_diluted_weighted_shares) and core.shares_outstanding_fallback. Refresh 'SEC filing index and reprocess' last 30 runs: median 79.7, p90 140.5, max 142.4 min; caps sum to 233 min > 180 timeout. Both must be fixed before the nightly flag switch.
