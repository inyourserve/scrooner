---
id: don-t-rank-or-filter-by-market-cap-without-a-san-747790
title: Don't rank or filter by `market_cap` without a sanity check first (found 2026-10-18)
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
Some values are impossible (AKTX $1.27T from ADS-underlying ordinary shares; TBLA/RPAY from diluted weighted-average share counts that look scale-wrong). Cloud sessions have no DB credentials in env, only the Supabase MCP `execute_sql`. It has a 60s hard cap, so `core.fact` joins over more than ~100 companies time out: chunk by company ids. Top-1000 campaign: `doc/data-moat/team/top1000/`.
