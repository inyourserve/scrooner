---
id: company-master-price-data-0b8d39
title: Company Master price data
kind: gotcha
tags: pipeline
paths: pipeline/CLAUDE.md
evidence: DOC-CITED
source: pipeline/CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
: `core.market_price_alpaca` (real, via Alpaca `delayed_sip`) is the only real price source — `core.market_price` still holds only mock rows from the pre-vendor-decision phase and must never be read as real.
