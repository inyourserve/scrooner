# 37. Strategy: becoming one of the best stock screeners (Ritwik, Head of Data Product, 2026-10-21)

Reports to: Dhairya (chief of staff). Status: v1. Read-only work: no DB writes, no code edits, no commits. DB queries skipped (17 connections on 2026-10-21, above the 14 limit), so every Scrooner count comes from a named repo file and is not a fresh measurement. Labels: FILING-CHECKED / DATA-INFERRED / ASSUMED / VENDOR-CLAIM.

## 0. The problem to solve (one sentence)
A serious US fundamental investor will only come back to Scrooner if every number on the page is right or visibly absent with a reason. Today we cannot say that for any company, and our own headline coverage number overstates what users see.

Evidence:
- Headline top-1000 fill is 80.86% (data-team/33 §0, DATA-INFERRED), but `coverage_matrix.py:746` counts a metric as filled if ANY period has a value while the reason comes from the LATEST period. Shards found 65-79 hidden blanks per 10 companies (code-read, data-team/33 §0). The real "current" fill is lower than 80.86%.
- Shard fill ranges 69.7% (S035) to 89.3% (S019), 84-243 unexplained blanks per 10 companies (doc/data-moat/team/top1000/status.md, 2026-10-18 baseline).
- Known wrong values exist: 10 wrong market caps in the ranking itself (S000, FILING-CHECKED), 7+ wrong values in S009, more in S012-S018 (status.md). 39 of 52,464 sampled rows differed from the authoritative copy (doc/data-moat/team/PLAN.md, DATA-INFERRED).
- Stale values shown as current: TMO gross margin 2019, INTU 2020, PANW debt FY2023 (data-team/33 §0, code-read).
- History 2015+: 96.5% present on only 15 core concepts (25,193 missing of 717,052); the other 18 consumed concepts and all metrics are unmeasured (data-team/34).

## 1. Decision sheet for the founder (three calls only you can make)
1. **Ship order: trust first, breadth second.** Recommendation: show a "Certified" badge only on companies that pass data-team/34; show everything else with a plain "unverified" label and reasoned blanks. Alternative: hide uncertified companies from public pages (hurts SEO, doc 01 moat 3). Would change my mind: if certification pace is under 25 companies/week by day 30.
2. **Scope of the first public promise.** Recommendation: promise "top 1,000 certified, history from 2015" and nothing wider until reached; keep the 5,216-company population visible but labelled. Alternative: promise all-company coverage (we cannot test it).
3. **First decision the product optimizes for** (doc 02 open question, doc 27): recommendation is "quality compounders" (ROIC, margins, FCF, share dilution, insider buying). Reason: these inputs are all EDGAR-native, already computed, and the least dependent on the price-vendor and bank-definition gaps. Alternatives: undervalued cash generators (needs market cap, currently the least trustworthy field), fast growers.

## 2. Users and the jobs (doc 01: serious self-directed US fundamental investor)
| Job | Metrics it needs | Trust level | Blocker today |
|---|---|---|---|
| Quality compounders | ROIC, ROE, gross/operating margin, FCF margin, revenue/EPS growth, share dilution | Very high: one wrong margin removes a stock from the list | Net income incl. NCI (family I), 606-subset revenue (G), partial-cost gross margin (N) |
| Undervalued cash generators | FCF yield, P/E, EV/EBITDA, net debt | Very high | Market cap/share-count errors (M), total_debt composition (D); EV/EBITDA not built |
| Dividend safety | payout, FCF cover, debt, dividend history | High | Dividend timing and per-class DPS (V); no-reason blanks |
| Insider/ownership-backed ideas | Form 4, 13F, N-PORT | High | Built; frontend Ownership section not built (CLAUDE.md) |
| Fast growers | revenue/EPS growth, margin trend | High | Q4 and quarter derivation gaps (5,801 + 5,345, data-team/34) |

## 3. Benchmark (thin; stated plainly)
I could not find independent accuracy testing for any competitor. What I found, all VENDOR-CLAIM or third-party review with commercial ties:
- Finviz: ~70 fixed filters, ~8 years history on the free tier; vendor says fundamentals come from Reuters and FactSet "verified" and "manual control"; a Trustpilot reviewer calls some fundamentals "blatantly incorrect" (single anecdote). Source: [Stock Rover's Finviz alternatives piece](https://www.stockrover.com/?p=46612) (publisher is a competitor), [Finviz Trustpilot](https://dk.trustpilot.com/review/finviz.com).
- Koyfin: free tier, paid roughly $39-79/mo, fund data gated at $209+/mo. Source: [toolradar](https://toolradar.com/compare/finviz-vs-koyfin) (VENDOR-CLAIM/aggregator).
- Screener.in (our stated feel reference): premium about ₹4,999/year, free tier, exports and multiple watchlists gated. Source: [strike.money review](https://www.strike.money/reviews/screener-in) (affiliate site, check Screener's own page).
- Common user-reported failure patterns across platforms: stale latest quarter, gaps in historical filings, occasional wrong values; the safe advice given is "check against SEC filings" ([Wealth-Lab forum](https://wl6.wealth-lab.com/Forum/Posts/Fundamentals-are-off-in-WLP5-28292)).
- NOT verified: FinChat, Simply Wall St, Morningstar, GuruFocus, TIKR, Bloomberg-class. Each needs a direct look at its pricing/data pages before we claim anything about them. No competitor metric should be copied until we confirm we can compute it correctly from EDGAR.

Read-across: every competitor sells breadth of metrics and a data vendor's word. None that I found shows the reader WHERE a number came from or that anyone checked it. That is the open lane.

## 4. Where Scrooner wins (and what to stop)
Deepen first, in order:
1. **Filing-level traceability on every number** (accession, locator, formula version, data date). Cheap for us, impossible for vendor-fed competitors to copy quickly.
2. **A visible certification state** per company (data-team/34: uncertified, checks_clean, reconciled, verified, certified). The honest differentiator: "this company's numbers were checked against its filings."
3. **Reasoned blanks.** "Bank revenue definition pending" beats a guess. Already pattern-proven by bank suppression (commits 5b96ff2, 153574d).
4. **Insider/institutional/fund ownership from SEC filings** (built). Doc 10 calls it the real differentiator.
5. **Plain-English screens with the interpreted query shown** (built, 6a/6b).
Stop or defer: new vendor data (analyst estimates, short interest, technicals; doc 02 excludes), adding metrics before the current 18 are certified, wider-than-top-1000 gap work, dimensional segment XBRL (doc 23: company-specific, not universal).

## 5. Coverage strategy
Coverage is a means to trust. Tiers:
| Tier | Companies | Promise | Gate |
|---|---|---|---|
| T1 | Top 100 by market cap (after S000 ranking fix) | Certified, 2015+ history, all 33 consumed concepts + 18 metrics | 100% cells valued or reasoned; Verifier filing check recorded |
| T2 | Top 1,000 (986 non-excluded) | Same, after T1 | data-team/34 definition |
| T3 | Remaining ~4,200 | Shown with "unverified" label; no certification claim; guard-suppressed where a detector fires | B1 guards only |
Rules: acceptable gap = company genuinely does not report the item (evidenced); unacceptable = unexplained blank, stale-as-current, or any unverified wrong value. Priority of work by decision value x reach: B0 measurement honesty, B1 serve-time guards, B2 real fixes (data-team/33 order is right; I endorse it).

## 6. Data-moat features users see (in build order)
1. "Why this number" panel: source filing link, period, formula, as-of date (small; data exists in lineage).
2. Certification badge + date on company page and in screener results; screener filter "certified only" (default ON for T1/T2 results).
3. Honest blank labels everywhere (reason text from the reason layer, B5).
4. Public data-quality scorecard: companies per state, open findings by family, wrong values found per 1,000 cells. Publishing our own error rate is the credibility move; no competitor does this (not verified exhaustively).
5. Restatement/change log per number (as-reported vs latest).
6. "Why this passed / nearly passed" screener panel (doc 27, extends built `excluded_missing_data`).
Ordering rationale: 1-3 cost little and make correctness visible before certification is complete; 4-6 need the certification tables (P1).

## 7. 30/60/90-day roadmap (owners = existing roles; dates ASSUMED)
| Window | Goal | Owner | Metric / baseline / target |
|---|---|---|---|
| Days 0-30 | B0 + B1: fix measurement (`has_value` = latest period), ingestion-gap detector, serve-time guards for stale, MCAP-SHARES, total_debt, 606, partial-cost | Data Engineer, Tag Mapper, Period Engineer | Baseline: "current fill" re-measured (expect below 80.86%); target: zero known wrong values displayed for T1 (100 cos); wrong values per 1,000 sampled cells: baseline 0.75 (39/52,464) -> under 0.1 |
| Days 31-60 | `scrooner-certify` (I1-I11) + SEC Financial Statement Data Sets reconciliation (R1); certify T1; B2 real fixes for total_debt, revenue precedence, net income attributable | Data Engineer, Standardization Lead (+ named accountant), Verifier | Certified companies: 0 -> 100; every T1 headline cell has a Verifier accession+locator |
| Days 61-90 | Certify T2 in batches of 10; bank/REIT/insurer templates (B3); "why this number" + badge + scorecard live | Sector Analyst, Verifier, Engineering | Certified: 100 -> 400+ (pace-dependent, ASSUMED 25-50/week); history completeness 2015+ extended to all 33 concepts |
Kill list: new metrics, T3 gap-chasing, yfinance as a verifier (signal only), more shards launched before the invariant suite exists (status.md still has 46 shards todo; running them without I1-I10 repeats work that code should do).

## 8. Team design
- Add nothing yet. The binding constraint is Verifier capacity (filing opening is the slow, human-grade step) and a named accountant for perimeter changes (data-team/34 P5).
- Measure each role: Verifier = filings checked/week and wrong rows found; Data Engineer = invariants shipped and cohort false-negative rate; Tag Mapper = mappings passing coexistence check; Triage = share of findings classified to a family.
- Retire per-company shard hunting as the primary loop: shards S020+ should become spot-check and exception work once `scrooner-certify` runs I1-I10 over all companies.
- Learning loop: tag findings to `data-team/tags/feedback-inbox.md`; product decisions to `strategy/LOG.md`.

## 9. Risks
- Sec.gov was blocked for several shards (S003-S008 "DATA-INFERRED only"), so many wrong-value claims lack filing proof. A certification built on inferred evidence would be a false promise.
- SEC companyfacts misses some 10-Q accessions (NEE, WELL, C, KO FILING-CHECKED), so "complete" needs a fallback reader that must match 100% on 50 filings first.
- The founder's "100% correct" is unprovable in absolute terms (data-team/34 honest limit: filer errors). Wording of the public promise matters; I recommend "checked against the filing" not "guaranteed correct".
- Concurrency: heavy DB jobs collide on a ~15-connection pooler; certification runs must be chunked and serialized.

## 10. What I could not verify
Fresh DB counts (pooler busy); FILING-CHECKED status for most shards; competitor data depth/pricing beyond the thin sources above; user demand (no usage data read; no analytics file reviewed); the 2026-10-21 current state of runs S020-S022.
