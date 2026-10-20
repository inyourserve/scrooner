# 37. Strategy: becoming one of the best stock screeners (Head of Data Product, 2026-10-21)

Status: v1 complete. Read-only work: no DB writes, no code edits, no commits. **DB queries were skipped**: `pg_stat_activity` showed 17 connections (twice), above the 14 limit. Every Scrooner count below is read from a repo file (named), not freshly measured. Evidence labels: FILING-CHECKED / DATA-INFERRED / ASSUMED / VENDOR-CLAIM. Includes the founder's 2026-10-21 History-window requirement (Jan 2015 to date, invariant I11, `data-team/34`).
Note: a peer session wrote a thinner draft to this same path at the same time; it is preserved unchanged as `37-ALT-PEER-DRAFT-RITWIK-2026-10-21.md`. Its useful extras (cell-overcount at `coverage_matrix.py:746`, the "why this passed / nearly passed" panel, competitor anecdotes) are consistent with this document.

## 0. Founder decision sheet (one page)

**The situation in four lines.** (1) Zero companies are certified today; the certification tables are an uncommitted migration (`0097_certification_tables.sql`, untracked in git status) and the invariant suite is uncommitted code. (2) The top-1000 campaign's shard table shows a mean of 78.5% of cells filled and about 137 unexplained blanks per 10 companies (about 8.4% of 1,630 cells), 2026-10-18 baseline (`doc/data-moat/team/top1000/status.md`, DATA-INFERRED; the peer draft quotes 80.86% from data-team/33, which per `coverage_matrix.py:746` overstates because any-period counts as filled). (3) Wrong-value families are FILING-CHECKED and hit the metrics investors screen on most (total debt, bank revenue, proxy net income, partial-cost gross margin, market-cap shares). (4) No retail screener page I could open advertises per-number filing provenance; that is the open lane (not verified by trial).

| # | Decision (founder only) | Recommendation | Cost | Risk |
|---|---|---|---|---|
| D1 | **Positioning and first winning job.** | "The screener whose numbers you can verify": certification plus per-number evidence for the top 1,000, aimed first at **compounders / quality** (ROIC, growth consistency, FCF every year, dilution) with **insider/ownership** as the free differentiator. Do not compete on estimates, real-time or global coverage. | No new spend; reorders work: certification before breadth. | Narrow at launch (top 1,000). Rest of the universe shown as "checks passed, not certified", never hidden. |
| D2 | **Display window and tiers.** | Data window **2015-01-01 to date** (about 11.8 years). Logged-out: last **7 fiscal years + 8 quarters**. Logged-in: the **full 2015 window**. **Retire the earlier "15 years logged-in" rule** (data cannot honor it). 10-year CAGR shown only when all 11 annual points are certified; default growth view 3y/5y. Optional: collect FY2014 as a growth base. | Small display work. FY2014 base cost unmeasured (ASSUMED modest). | Public 7y is richer than Finviz free (3y), Koyfin free (2y), TIKR free (5y) and may cut upgrades. Test, do not assume. |
| D3 | **Freeze breadth, name an accounting reviewer, set the release rule.** | (a) Freeze new metrics, sectors and sources until **300 companies are certified** (day 60). (b) Name one human accounting reviewer (doc 02 / data-team/34 P5 need one for perimeter changes). (c) Show a number only if it passes I1-I11, else a reasoned blank; companies outside the top 1,000 keep "checks passed" wording. | Reviewer hours (ASSUMED a few per week). About 60 days with no new features. | Founder fatigue. Mitigation: visible trust features ship in that window (section 5). |

**Bet in plain words.** The moat is not how many numbers we hold; it is that every shown number is right and can be opened to its filing. Competitors win on estimates, real-time and global breadth, which EDGAR cannot give us.

## 1. Users and jobs

User (doc 01): serious self-directed US fundamental investor; not day traders or institutions. Doc 27's open question (which decision the first screen optimises) is closed by D1.

Metric names from `mapper/definitions.py` (V1 18), `mapper/expanded_metrics.py` and `doc/status/DATA_COVERAGE.md` (registry 82 metrics, 71 concepts per that file's 2026-09 entry; the current `analytics.metric_definition` count could not be queried).

| Job | Metrics needed | Trust level | Serve correctly today? (evidence) |
|---|---|---|---|
| J1 Compounders / quality | roic, roe, revenue_growth_3y_cagr, eps_growth_3y_cagr, fcf_margin, fcf every year, share_dilution_trend, operating_margin, gross_margin, piotroski_f_score; 5-10 clean annuals | Highest: one bad year breaks the screen | **No.** ROIC needs total_debt (wrong for LLY, RTX, ABBV, CSCO, TMO, FILING-CHECKED, VERIFY-W1) and operating income (GE 22,887M is a FY2012 segment figure). Partial-cost gross margin (UNH, CVX). |
| J2 Undervalued cash generators | fcf_yield, ev_ebitda, ev_sales, trailing_pe, price_to_book, net_debt_ebitda, market_cap | High | **No.** Market cap rests on shares (SHOP stored 0 vs 1.29B cover page, FILING-CHECKED; 10 wrong market caps in S000); EV rests on total_debt. |
| J3 Fast growers | revenue_growth_yoy, eps_growth_yoy, margins trend, dilution, SBC % revenue; quarterly history | High | **Partial.** Revenue precedence (AXP segment 11,212M vs face 19,637M, FILING-CHECKED); derived Q4 EPS wrong (KLAC, FILING-CHECKED). |
| J4 Dividend safety | dividend_yield, dividends_pct_fcf, interest_coverage_ratio, debt_to_ebitda, current_ratio | High | **Partial.** Dividend timing family V open (data-team/33); DHR and C paid dividends but showed blank (FILING-CHECKED). |
| J5 Balance-sheet safety | debt_to_equity, current_ratio, net_cash, zero_debt, quick_ratio, piotroski | Highest (false "zero debt" is harmful) | **No.** ABBV total debt 0 vs 70,822M (FILING-CHECKED). |
| J6 Insider / ownership ideas | Form 4 with 10b5-1 flag, institutional_ownership_pct, N-PORT, 13D/G | High; filing-parsed, no accounting judgment | **Closest.** Built, golden-10 verified, scaled 2026-08-29 (CLAUDE.md, doc 19); not re-checked in the top-1000 campaign (ASSUMED sound). 688 implausible institutional % values are guarded (DATA_COVERAGE). Frontend Ownership section not built. |

**Reading.** No job is certifiably served today. J1, J2, J5 share one root: total_debt and operating income. The total_debt rebuild (data-team/33 batch B2) is the highest value per unit cost.

## 2. Benchmark (accessed 2026-10-21; VENDOR-CLAIM unless noted)

| Product | History / depth | Catalog | Trust, provenance, point-in-time | UX | Price | Source |
|---|---|---|---|---|---|---|
| Screener.in | "10 years of financial data" | Query language; no company count | Footer: data by C-MOTS; no per-number source on page | Text queries; 50-company cap on free (third-party) | Premium about INR 4,999/yr (search snippet; `/pricing` 404) | screener.in homepage; strike.money review |
| Finviz | Free 3y / Elite 8y statements | "20+ advanced" filters Elite | Not mentioned | 50 presets free, unlimited Elite; real-time on Elite | Elite $24.96/mo annual, or $299.50/yr, $39.50/mo | finviz.com/elite.ashx |
| Koyfin | Free 2y; Plus 10y financials and estimates | "100K+ global company snapshots" | PIT not mentioned | Free 2 screens; Plus unlimited | Plus $39/mo; Premium $79; Advisor $209-299 | koyfin.com/pricing |
| TIKR | Free 5Y/8Q; Plus 10Y/20Q; Pro 10Y/40Q; Ultimate 30Y/40Q | Free US only; paid global; provider unnamed | Not stated | Saved screens 1/10/30/unlimited | $24.95 / $54.95 / $119.95 per month | tikr.com/pricing |
| Stock Analysis | Pro "10-40 years and growing"; "130,000+ global stocks and funds" | "300+ indicators" | Provider unnamed | Save screeners | Pro $79/yr or $9.99/mo | stockanalysis.com/pro |
| GuruFocus | "30 years" Premium; backtesting from 2006 on Premium Plus (snippets; fetch 403) | Large global | PIT / restated vs as-reported: not found in any source | Backtesting | About $424-549/yr Premium, $1,273-1,348 Plus (conflicting) | gurufocus.com/pricing (snippet) |
| Seeking Alpha | One review: 10 years downloadable statements | Quant Ratings, screener | Ratings claims vendor-friendly | Screener by rating, yield | Premium about $299/yr; Pro $2,400/yr (reviews) | financer.com (snippet) |
| Morningstar Investor | 10-year financials not confirmed | "200+ fields"; fair value on about 1,500-1,800 US stocks | Analyst ratings | Cannot filter arbitrary metrics (review) | $34.95/mo or $249/yr (reviews) | snippets only |
| Simply Wall St | Not found | Not found | Provider not confirmed | Not found | About $120/yr Premium, $240/yr Unlimited (their comparison page, snippet) | snippet (pricing 404) |
| FinChat | Not found | Not found | "Sourced answers", mechanism unverified | AI chat | About $50/mo, unverified catalogue estimate | pricing page 403 |
| Institutional: S&P Compustat | Annual from 1950, quarterly from 1962; **point-in-time Snapshot since 1987, interim 1996**; originally reported and restated | n/a | Only product with documented PIT and restatement | n/a | Institutional licence | marketplace.spglobal.com; WRDS webinar PDF (search) |
| Public primary: SEC Financial Statement Data Sets | Jan 2009 to Sep 2026, quarterly; "as filed"; reprocessed Dec 2024 | n/a | Free, as filed | n/a | Free | sec.gov data sets page (fetched) |

**Could not open:** FinChat pricing (403); GuruFocus pricing (403); Simply Wall St pricing (404); Screener.in `/pricing` (404). Morningstar, Seeking Alpha, Simply Wall St, FinChat feature pages not opened (reviews and snippets only, weak). Bloomberg not checked. No product trial of any screener. The peer draft cites a Finviz anecdote (Trustpilot) and Stock Rover pieces; not re-verified here.

### 2a. How the 2015-onward window changes the benchmark
- About 11.8 years **meets the 10-year paid tier** of Koyfin Plus, TIKR Plus/Pro, Stock Analysis Pro, Screener.in, and exceeds Finviz Elite's 8. It is **below** TIKR Ultimate 30Y, GuruFocus 30y, Stock Analysis up to 40, Compustat 1950. Depth is parity, not a differentiator.
- Retail paid prices cluster at roughly **$75-$300/yr** (Stock Analysis $79, Simply Wall St about $120, Morningstar $249, Seeking Alpha $299, Finviz $299.50). The $100/yr hypothesis (doc 01) sits inside. Competitors with 10+ years: Koyfin Plus ($39/mo), TIKR Plus ($24.95/mo), Stock Analysis Pro, GuruFocus, Seeking Alpha (reported).
- **Point-in-time and restatement history:** no retail page I could read mentions it; only Compustat documents it. `core.fact` keeps filing and `supersedes_fact_id` (infra map §3), so as-first-reported vs restated looks feasible from our tables (ASSUMED until prototyped). Cheap to claim, hard to copy, only for 2015+, and only with a restatement log (F4).
- SEC Data Sets reach back to 2009, so independent reconciliation (R1, data-team/34) covers the whole window.

## 3. Where Scrooner wins, and where it cannot

**Cannot win:** analyst estimates and targets (doc 02 exclusion; Koyfin, TIKR, SA have them); real-time quotes (Alpaca delayed SIP, doc 25); non-US and foreign private issuers (doc 02); history before 2015 and 30-year depth; analyst ratings (Morningstar, SA Quant); technicals; indicator breadth (Stock Analysis claims 300+); brand and community. Do not spend here.

**Can win, ranked by defensibility then cost (sizes ASSUMED):**
| Rank | Lever | Defensibility | Cost | State |
|---|---|---|---|---|
| 1 | Certified correctness, visible (badge, I1-I11 suite, FILING-CHECKED headline cells) | Very high: needs process, not code | High (60-90 days) | 0 certified; suite uncommitted |
| 2 | Per-number "why this number" | High: needs lineage we have (`source_fact_ids`, metric `fact_ids`) | Medium | Not built; only filings list, insider and 13D rows link to sec.gov (`stocks/[ticker]/page.tsx:70`); null-reason tooltip exists (`MetricGrid.tsx:23`) |
| 3 | Blank-with-reason, never a guess | High culturally | Low | Metric reasons exist; unexplained blanks about 8.4% |
| 4 | Restatement and change log | High; no retail competitor found documenting it | Medium | Data likely supports; UI and diff job absent |
| 5 | Filing-derived ownership and insider data | Medium | Low | Built |
| 6 | Plain-English screens with visible interpreted query | Low-medium (AI assist copyable) | Built (6a/6b) | Wedge, not moat |
| 7 | Free data cost (EDGAR) | Structural | n/a | Holds |

Levers 1-4 are one trust system; build as one product.

## 4. Coverage strategy

Standard (data-team/34): every displayed value correct, or visibly unavailable with a reason.

| Tier | Companies | State | Date |
|---|---|---|---|
| T1 | Top 100 | `certified` (I1-I11 across 2015+ plus Verifier headline check) | day 45 |
| T2 | Top 1,000 (986 non-excluded, shards.csv) | 300 certified day 60, 700 day 90, rest `reconciled` | day 90 |
| T3 | About 3,000 | `checks_clean`; not called certified | after day 90 |
| T4 | All, about 4,817 real operating companies (DATA_COVERAGE 2026-09) | "As filed, checks passed"; wrong values suppressed; no coverage promise | continuous |

**Certify first, by jobs served per rule family fixed:** (1) total_debt composition (debt_to_equity, net_debt_ebitda, debt_to_ebitda, ev_*, roic, zero_debt: 4 jobs); (2) revenue (606 vs total; bank/financial definition) feeding every margin and growth metric; (3) net income attributable and EPS, never by subtraction; (4) shares and market cap (cover-page sum, ADS, stale guard); (5) operating income / EBITDA inputs; (6) CFO and capex (additive allowlist); (7) dividends and buybacks. This matches data-team/33 B0-B4 with explicit job mapping.

**Cut or show with a reason:** keep bank suppression (5b96ff2, 153574d); extend the "family not yet supported" reason to insurers, REITs where a metric is meaningless; add no metrics beyond the 82; pause the 10 face-line concepts that feed no metric (PLAN.md: 45 of 78 concepts feed no metric).

**Acceptable gap standard**
| Gap | OK? | Evidence required |
|---|---|---|
| Not reported / not applicable to family | Yes | Sector template or rendered statement; `no_line_item_filed` alone is not enough (18% of a rendered sample showed the line, CLAUDE.md) |
| Not yet public / registered {date} | Yes | First filing date or predecessor CIK |
| Not in SEC feed | Temporary | Accession; instance-file/FSDS fallback (NEE, WELL, C, KO, VERIFY-W2) |
| Definition pending | Yes, labelled | Named reviewer ticket |
| Unexplained blank | **No** | Blocks `certified` |
| Wrong value | **No** | Suppress first, then fix |

**History completeness (I11) in the metric.** Report per company present / expected periods since 2015-01-01, every missing cell classified. Baseline 96.5% of 717,052, 15 concepts (data-team/34, DATA-INFERRED). Causes: q4_not_derived 5,801, quarter_not_derived 5,345, no_mapped_tag about 8,600 (era tags), no_line_item_filed about 1,700, not_in_sec_feed about 1,500, conflict_material 566, filing_not_processed about 850. Extending to 33 concepts and metrics will lower the number; report as a re-baseline, not a regression.

## 5. Data-moat strategy: visible trust features

Exists (checked in repo): `apps/app/app/methodology/page.tsx` and `data-sources/page.tsx` (prose); `app/app/data-coverage/page.tsx` (logged-in pipeline-health scores, not per-company certification); `components/company/MetricGrid.tsx` null-reason tooltip; filings, insider, 13D rows linking to sec.gov by accession (`stocks/[ticker]/page.tsx:70-110`, `lib/company/db.ts`). **Absent:** per-number provenance, certification badge, public scorecard, restatement log, corrections policy.

| Feature | User sees | Engineering | Reuses | When |
|---|---|---|---|---|
| F1 Certification badge | "Certified {date}: N cells checked, M filings opened" and state | Read `analytics.company_certification` (migration 0097, untracked) in `lib/company/db.ts`; badge component; 5 states | data-coverage patterns | day 30 pilot |
| F2 Why this number | Click a value: form, accession, link, period, tag, formula and inputs with their filings, data date; derived Q4 shows arithmetic | Endpoint in `apps/backend/company_page.py` resolving `canonical_fact.source_fact_ids` and metric fact_ids to `core.filing.accession_number`; panel | `secUrl()` helper | T1 day 45; 1,000 by day 75 |
| F3 Public scorecard | `/data-quality`: certified count, wrong values found/fixed per month, blank-with-reason share, latency, open findings by family | Weekly snapshot table + static page | `coverage_snapshot` | day 60 |
| F4 Restatement and change log | "Originally X, restated to Y in filing Z"; recent-changes feed | Job diffing supersession chains and canonical_fact changes; a conflict is not a restatement (infra map §2) | `supersedes_fact_id` | day 90 prototype |
| F5 Corrections policy | How to report, acknowledgement target, dated corrections | Policy text (founder), contact path, log; each fix becomes a ledger entry (data-team/22) | ledger | text day 30, log day 60 |
| F6 "Why passed / nearly passed" (peer draft, doc 27) | Screener transparency panel | Extends built `excluded_missing_data` | screener | after F2 |

Rules: show only what checks proved ("certification proves the checks and the sampled filing comparison pass; it cannot prove the filer's own filing is right"); never "guaranteed". Filer errors (GE quarterly revenue double tagging, FILING-CHECKED, data-team/35) appear as documented company exceptions.

## 6. 30/60/90-day roadmap

Owners are the existing roles: Data Chief, Data Engineer, Tag Mapper/Tag Expert, Period Engineer, Standardization Lead (+ accountant), Sector Analyst, Data Verifier, Data Triage, Head of Data Product (gates), engineering.

| Gate | Baseline (source) | Day 30 | Day 60 | Day 90 |
|---|---|---|---|---|
| Certified companies, top 1,000 | **0** (migration 0097 untracked, git status 2026-10-21) | 10 pilot | 300 (T1 100 by day 45) | 700; rest reconciled |
| Wrong values per 1,000 cells, I1-I11 over the 2015 window | **Not measured**; first suite run is the baseline | Baseline per family published | <= 2.0 on T1 | <= 0.5 on T1+T2; **0 open wrong_value on any certified company** |
| Blank-with-reason share | Unexplained about 137 per 10 companies = 8.4% of 1,630 cells; mean filled 78.5% (status.md 2026-10-18) | 95% on pilot | 100% classified on T1 | 100% classified on T1+T2 (only acceptable certified state) |
| History completeness I11 | 96.5% of 717,052 on 15 concepts (data-team/34) | Extend to 33 concepts + metrics, re-baseline | >= 99.0% present, 100% of missing classified (T1) | >= 99.0% on T2; 100% filled-or-classified |
| Filing-to-display latency p50/p95 (top 1,000) | **Not measured**; daily refresh 12:23 UTC (pipeline-refresh.yml) plus SEC companyfacts lag; feed gaps NEE, WELL, C, KO | Measurement built | p50 <= 24h, p95 <= 72h | same, plus feed-gap fallback live |

**Days 1-30: measurable and stop the bleeding.** (1) Commit and apply certification migration and `scrooner-certify` I1-I10; add I11 (extend `period_completeness` from 15 to 33 concepts and metrics) (Data Engineer, Verifier review); run on top 100. (2) B0/B1 (data-team/33): fix `coverage_matrix.py:746` any-period overcount, ingestion-gap detector (P3), serve-time guards turning wrong values into reasoned blanks. (3) total_debt rebuild dry-run, Verifier sample with zero wrong rows, accountant for perimeter (Tag Mapper, Standardization Lead). (4) Predecessor/successor CIK links for MRVL, LIN, SHOP, BLK, DIS, XOM and the foreign-private-issuer population check (Data Engineer, Company Master). (5) Corrections policy text and badge component. (6) Verifier trial of 10 companies at 2015, 2018, 2021, 2025 annual values.
**Days 31-60.** Revenue precedence, net income attributable, shares/market cap guard; era-scoped tags FY2015-2018 (Tag Expert cards record era); Q4/interim derivation on the additive allowlist (Period Engineer); split table complete 2015+; R1 reconciliation vs SEC FSDS for top 1,000; F2 for T1; F3; 300 certified.
**Days 61-90.** Sector templates (banks, broker/asset manager, insurer, REIT) with the accountant; F2 to 1,000; F4 prototype; incremental nightly cohort selection and non-overlapping jobs (P8); 700 certified; decision review on T3.

**Kill list.** (1) New metrics, unmapped-tag work feeding no metric, new data sources, DEF 14A, dimensional XBRL, B2B API, until 300 certified. (2) "Coverage %" as the headline (circular denominator, CLAUDE.md 2026-10-17; replace with certified count and wrong per 1,000). (3) yfinance as anything but a signal. (4) "Latest filed wins" without original-filing validation (CLAUDE.md 2026-10-18). (5) The 15-year tier. (6) Launching more shards (46 still todo in status.md) before the invariant suite exists. (7) Promising a number for the all-companies tier.

### 6a. History window: what is realistic
- **Window:** 2015-01-01 to latest filed period, about 11.8 years, inside the XBRL era (SEC Data Sets from Jan 2009).
- **Pre-2018 filers (FY2015-FY2018):** about 8,600 gaps are `no_mapped_tag` because those filers used different tags (era-scoped tags needed). Realistic target: 99% present with 100% classified, not 100% filled; remainder are custom tags or genuine absences. Q4 only by the additive allowlist; EPS and shares never by subtraction.
- **Companies registered after 2015:** history starts at first filing; earlier periods carry `not yet public / registered {date}` (legitimate). A first 10-K's prior-year comparatives are usable only tied to that filing and labelled. 113 companies have earliest core.period after 2018 (data-team/34).
- **Re-registered under a new CIK (MRVL, LIN, SHOP, BLK, DIS, XOM, the founder's list; I did not verify each CIK history, ASSUMED):** history joins only through an explicit predecessor/successor link in Company Master with evidence (successor 10-K or 8-K naming the predecessor), labelled "reported by predecessor CIK {x}". Do not link where the transaction changes the reporting entity (acquirer/acquiree). SHOP's stored 2016 20-F zero share class (FILING-CHECKED, VERIFY-W2) shows foreign-form history is not usable as us-gaap data; its pre-10-K years may stay blank-with-reason. Expect these six to stay `verified`, not `certified`, until each link is Verifier-checked.
- **Promise to a user:** "Complete from 2015 or from first public filing, every gap explained." Never "complete history."

### 6b. Display tiers
- **Logged-out:** 7 fiscal years + 8 quarters (the 2026-08-23 decision, `memory/project_data_depth_tiering.md`, mirroring Screener.in). **Logged-in:** the full 2015 window (about 11-12 fiscal years, 40+ quarters). "Up to 15 years" is superseded.
- **10-year CAGR works at the 2015 start:** FY2025 vs FY2015 uses 11 annual points, all inside the window (a Jan-31 year-end company's FY2014 ends 2015-01-31, also inside). No slack: any gap in 11 points blanks it, and FY2015 YoY and 3y/5y at the window start have no base. Rule: show 10y CAGR only if all 11 annuals are certified, else "needs 11 certified years"; default to 3y/5y; label first-year growth "history begins 2015". Optional FY2014 hidden base for FY2015 YoY. Next year the window rolls (FY2026 vs FY2016), still inside.
- **Paywall logic:** competitors gate depth (Finviz 3y/8y, Koyfin 2y/10y, TIKR 5Y/10Y/30Y). Years are parity; the paid hook should be saved screens, exports, alerts and F2/F4 depth. Test conversion.

## 7. Team design

| Role | Action | Measured on | Learning loop input |
|---|---|---|---|
| Data Chief | Keep | Gate attainment | Weekly gate review |
| Data Verifier | **Grow**: bottleneck (the peer draft agrees: filing opening is the slow step); add a lane for R1/FSDS reconciliation review | Companies verified/week; wrong rows found in samples; zero false "verified" | Every case to ledger data-team/22 |
| Data Engineer | Keep; owns `scrooner-certify`, I11, F2 endpoint | Suite runtime; latency; no regressions | Incident reviews |
| Tag Expert / Tag Mapper | Keep; add **era** to every tag card | Wrong mappings found by Verifier (0 on 12-case samples) | `tags/feedback-inbox.md` |
| Period Engineer | Keep; Q4 derivation across 2015+ | q4/quarter_not_derived (5,801 / 5,345) | Ledger |
| Standardization Lead | Keep; proposals only | Decisions closed/week | Decision log |
| Sector Analyst | Keep; banks first | Families supported; suppression correct | Template tests |
| Data Triage | **Retire the coverage-gap ticket stream**; repurpose to classify missing cells into I11 causes and dedupe | Unclassified cells (0) | Disagreements to Verifier |
| Head of Data Product | Keep; scorecard and kill list | Scorecard on time | strategy/LOG.md |
| **Add:** named accounting reviewer (human, part-time) | Add | Turnaround on definition tickets | doc 02 |
| **Add:** corrections owner | Add after F5 | Time to acknowledge/fix | Corrections log to ledger |

Learning loop: each wrong value found anywhere becomes (1) a ledger entry with accession, (2) a suite rule if code can catch it, (3) a Tag Expert card update if tag-related. Metric: share of new wrong values a suite rule would now catch (> 80% by day 90). Roles are judged on wrong values let through, not tickets closed.

## 8. Risks and what would change my mind
| Risk | Evidence that changes the plan |
|---|---|
| Certification slower than 300 by day 60 | If pilot companies take > 2 days each, cut T1 to 50 and narrow the claim to headline metrics |
| 7y public depth cuts upgrades | A/B test; if signup-to-paid falls, drop to 5y |
| Suite false findings | If > 20% false on a Verifier sample, tune before gating |
| Users don't value provenance | If < 5% of sessions open F2 or badge in 60 days, shift weight to J6 and valuation screens |
| Latency dominated by SEC companyfacts lag | If p95 > 72h from SEC side, build instance-file/FSDS fallback earlier (P3) |
| Mis-linked predecessor CIKs | Verifier checks each; a mis-link blocks certification |
| Competitors add provenance | Lean on restatement log and certification process |
| Sec.gov blocked for shards (S003-S008 DATA-INFERRED only, peer draft) | A certification on inferred evidence would be a false promise; Verifier lane required |
| Connection/DB collisions | 17 connections today; serialization (f56c6a6) must hold |
| Unverified benchmark | Pages and reviews, not trials; a trial showing per-number source filings elsewhere weakens lever 2 |

## 9. Sources and what I could not verify
**Fetched 2026-10-21:** screener.in homepage, finviz.com/elite.ashx, koyfin.com/pricing, tikr.com/pricing, stockanalysis.com/pro, sec.gov Financial Statement Data Sets page. **Search snippets only:** Screener.in price (strike.money), GuruFocus, Seeking Alpha (financer.com), Morningstar (review sites), Simply Wall St, Compustat (marketplace.spglobal.com, WRDS), FinChat. **Blocked/missing:** screener.in/pricing 404; gurufocus.com/pricing 403; finchat.io/pricing 403; simplywall.st/pricing 404.
**Repo:** CLAUDE.md; data-team/09, 20, 22, 33, 34, 35; doc/data-moat/team/PLAN.md; top1000/status.md, shards.csv; doc/status/DATA_COVERAGE.md; doc 01, 02; `mapper/definitions.py`; the `apps/app` files named; git status 2026-10-21.
**Not verified:** current DB counts (skipped); the exact 82-metric list and per-metric coverage; whether `core.fact` yields as-first-reported cleanly; wrong-values-per-1,000 baseline; latency; CIK histories of the six companies; docs 26 and 27 read only through CLAUDE.md summaries; demand and willingness to pay; any competitor's in-product provenance; Compustat claims are VENDOR-CLAIM.
