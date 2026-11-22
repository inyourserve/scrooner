---
id: core-fact-has-no-extension-taxonomy-facts-cross-filing-value
title: core.fact has no extension-taxonomy facts; cross-filing value conflicts leave no authoritative copy
kind: gotcha
evidence: DATA-INFERRED
status: active
created: 2026-11-12
verified: 2026-11-12
---
Engineering 2026-11-12: core.fact taxonomies are us-gaap/dei/ifrs-full/ecd/srt/invest only (SEC companyfacts carries no company extension tags), so custom-tag face lines read fsn.value (founder decision 2026-11-12, doc 02). Separately, when filings disagree on a period (rounding, e.g. PANW $M vs $K; restatement, e.g. MSFT S&M 14,697 vs 14,635 in the FY2018 10-K) the resolver marks no copy authoritative, so every sum touching it is held. Dhairya ruling 2026-11-12: most precise copy wins within the coarser decimals; beyond that the latest accepted filing wins (doc 02, 2026-11-01 item 3); Engineering owns the resolver.
