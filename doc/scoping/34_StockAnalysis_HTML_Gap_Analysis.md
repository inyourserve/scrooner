# Doc 34 — StockAnalysis.com HTML Gap Analysis

**Status: Draft (2026-08-28) — a scoping proposal, not a build plan.** Five real StockAnalysis.com pages for NVIDIA (NVDA) — `doc/html/stock analysis/overvuew,html`, `profile.html`, `metricks.html`, `dividend.html`, `financials.html` — were read in full (HTML stripped to visible text, not recalled from memory) and cross-referenced against the actual current pipeline code, not the docs' own summaries of it. This supersedes and deepens doc 30's own Track 7 pass over the *same five files* (2026-08-24) — Track 7 was a same-session quick scan; this pass re-reads every page in full and verifies each candidate directly against `pipeline/src/scrooner_pipeline/mapper/expanded_definitions.py`, `mapper/calculate.py`, `mapper/expanded_concepts.py`, `mapper/definitions.py`, `mapper/ttm.py`, `mapper/concepts.py`, `statements/classify.py`, `normalizer/identity.py`, the `core.company` migration files, and `apps/site/src/lib/prosCons.ts` — not assumed from Track 7's own bullet points. Two of Track 7's items turn out to already be built (research & development, interest income — via doc 28, landed 2026-08-21, three days *before* Track 7 ran but not called out there since Track 7 was scoped to new items); one genuinely new candidate not named by Track 7 or any prior doc is surfaced below (cover-page address/phone `dei` tags).

Per standing project discipline (docs 26/28/30/31): only SEC/free-official sources are in scope. Anything StockAnalysis.com's own page footer attributes to a named paid vendor (S&P Global Market Intelligence, Fiscal.ai, TipRanks, EOD Historical Data, CBOE, Nasdaq UTP) is flagged as out of scope, not proposed for building — a real competitor's own sourcing disclosure is stronger evidence of "needs a vendor" than an API check alone, the same reasoning doc 30 Track 7 already used for TipRanks.

---

## 1. What StockAnalysis shows that Scrooner already has (no gap)

Checked line-by-line against the current code, not the docs' own summaries — several of these are *more complete* than what a first skim would suggest:

| StockAnalysis field | Scrooner status | Evidence |
|---|---|---|
| Market Cap, PE Ratio, Dividend ($/yield) | ✅ `price_metrics.py` (doc 25) | `mapper/definitions.py` `market_cap`/`trailing_pe`/`dividend_yield` |
| Revenue, Net Income, EPS + growth | ✅ Locked V1 metrics + expanded growth | `revenue_growth_yoy/3y/5y/10y_cagr`, `eps_growth_yoy/3y/5y/10y_cagr` in `mapper/ttm.py`'s `GROWTH_METRICS` |
| Shares Out | ✅ `shares_outstanding` canonical concept, incl. multi-class fallback (`company_master/shares_outstanding_fallback.py`) |
| Gross/Operating/Profit(Net) Margin, FCF Margin | ✅ `mapper/definitions.py` (`gross_margin`, `operating_margin`, `net_margin`, `fcf_margin`) |
| Revenue, Gross Profit, Operating Income, Net Income, EPS annual series (Financials page) | ✅ Same locked concepts, any period | — |
| Cash & Investments (as `cash_and_equivalents`), Total Debt | ✅ Both mapped concepts (`mapper/concepts.py` lines 39/83; `expanded_definitions.py`'s `net_debt_ebitda`) |
| Operating Cash Flow, CapEx, Free Cash Flow | ✅ `cfo`, `capex`, `fcf` (`mapper/definitions.py`) |
| P/FCF Ratio via FCF Yield, PS Ratio (Price/Sales) | ✅ `fcf_yield`, `price_to_sales` |
| PEG Ratio | ✅ `expanded_definitions.py`'s `peg_ratio` (doc 18 Tier A) |
| Dividend Yield, Annual Dividend, Payout Frequency (quarterly cadence is derivable from `dividends_per_share`'s own period pattern) | ✅ |
| Buyback Yield, Shareholder Yield | ✅ `expanded_definitions.py` (`buyback_yield`, `total_shareholder_yield`) |
| Dividend Growth Years (StockAnalysis: "Growth Years: 2") | ✅ `dividend_growth_streak_years` (`mapper/dividend_streak.py`) |
| Industry, Sector | ✅ `core.company.sic_code`/`sic_description` (Company Master 4a) |
| Employer's SIC Code | ✅ Same field, e.g. NVDA's `3674` matches exactly |
| Ticker Symbol, Exchange, Stock Type (Common Stock) | ✅ `core.listing` + `security_type` via OpenFIGI (doc 25) |
| CIK Code | ✅ `core.company.cik` |
| Recent SEC Filings: 8-K, 13F-HR (as a general form type), DEF 14A-family | ✅ `normalizer/identity.py`'s `FORM_ALLOWLIST` already includes `8-K`, `8-K/A`, `15-*` family, `SC 14D9`, `DEF 14A`/`DEFA14A`/`DEFM14A`/`DEFR14A` — **this is more complete than doc 30/31 gave it credit for as of this pass**; Form 15 and SC 14D9 (doc 23's items) are in fact already live in the allowlist, not merely scoped |
| Company Description ("About NVDA") | ✅ Explicitly out of scope by design (`apps/site` "must never fabricate a value like About text with no real data source" — root `CLAUDE.md`) — StockAnalysis itself sources this from S&P Global Market Intelligence, confirming it needs a vendor, not a gap in our own build |

**Correction to doc 30 Track 7:** Track 7 (2026-08-24) listed R&D and Interest Income among StockAnalysis's "genuinely new, free/SEC-native items" without noting they were already built. Checked live in code (not the doc): `research_and_development` and `interest_income` were added to `mapper/expanded_concepts.py` on **2026-08-21**, three days *before* Track 7 ran, per doc 28's own item #1/#4 recommendations — `rnd_intensity` and `net_interest_income` are both real, seeded `metric_definition` rows today. Not a new finding; confirming an already-closed one.

---

## 2. Deliberately excluded already — confirmed against doc 02 and the pages' own vendor disclosures

| StockAnalysis section | Why it's out of scope |
|---|---|
| Real-time price, Volume, Open, Previous Close, Day's Range, After-hours price | doc 02's price-vendor decision is delayed data (Alpaca `delayed_sip`), not intraday/real-time — explicit MVP exclusion |
| 52-Week Range, Beta (as shown here — a single number, not the fundamental-adjacent framing doc 28 already raised) | Needs historical price series Scrooner doesn't yet ingest (doc 25 §2's snapshot-only scope) — matches doc 26 §4's already-named gap |
| Analysts: Strong Buy / Price Target / consensus, Forward PE, Earnings Date (forward-looking) | Analyst estimates — explicit MVP exclusion (doc 02), same as doc 18 Tier C |
| News feed, "Financial Performance"/"Analyst Summary" narrative blurbs | Editorial/generated content, not a data point; several items explicitly credited to TipRanks in the page's own byline |
| **Revenue by Market Platform, Data Center Revenue Breakdown, Operating Income by Segment, Revenue by Geography, Operating Expense Breakdown** (Metrics page) | Page footer states outright: **"Business metrics are provided by TipRanks and sourced from official company press releases and documents."** Stronger than an API check — the competitor's own page names the paid vendor it needed. Consistent with doc 22/23's "dimensional/segment XBRL is a real, hard, company-specific-extension problem" finding. |
| **Revenue by Segment (Compute & Networking / Graphics), 2-segment split on the Financials page** | A more specific finding this pass: this simpler top-level segment table is *not* attributed to TipRanks — the Financials page footer instead credits it to **Fiscal.ai** ("Revenue segment data is provided by Fiscal.ai"). Different named vendor, same conclusion: even NVDA's simplest 2-way segment split isn't sourced from a page that claims to parse EDGAR directly. Consistent with, not contradicting, doc 22's dimensional-XBRL-is-hard finding — worth recording that StockAnalysis needed a vendor for even the coarsest segment cut, not just the granular one. |
| Executive officer roster/bios (Key Executives table, Profile page) | Page footer: "sourced from EOD Historical Data" — a named third-party vendor, not EDGAR-direct. Matches doc 22/28's unstructured-text-parsing bucket (would need DEF 14A/10-K free-text parsing even if built ourselves, still P2 per doc 19 Stage 5) |
| Company Founded date, Country, CEO name, Website (Profile page) | Page footer: "provided by S&P Global Market Intelligence" — explicitly named vendor |
| CUSIP Number, ISIN Number (Profile page's Stock Details) | Not `dei`-taxonomy XBRL tags; ISIN in particular has no EDGAR source at all. (NVDA's own CUSIP does appear incidentally in `core.beneficial_ownership.cusip` *if and only if* a Schedule 13D/13G was ever filed naming NVDA as subject company — not a general per-company field today, and not worth building as one just for this) |
| Dividend Record Date / Pay Date columns (Dividend page's history table) | Confirmed via direct page read: StockAnalysis shows all four columns (Ex-Dividend Date, Cash Amount, Record Date, Pay Date) per dividend event, all four sourced from S&P Global Market Intelligence per the footer. Only the per-event Cash Amount is free/already built (`dividends_per_share`) — Record/Pay dates aren't standard `us-gaap` XBRL tags; they'd need real 8-K/press-release text parsing, the same deferred territory as doc 19 Stage 5. Confirms, doesn't newly discover, doc 30 Track 7's finding — now with the actual 4-column table structure verified rather than inferred. |

---

## 3. Genuinely new, real, and feasible — ranked by verified value

### 1. Cover-page contact `dei` tags: Address, City/State/Zip, Phone — **not named by any prior doc analysis of this project**
The Profile page's "Contact Details" block shows a full mailing address (2788 San Tomas Expressway, Santa Clara CA 95051) and phone number (408 486 2000). These map to standard SEC cover-page `dei` tags used on virtually every 10-K/10-Q — `dei:EntityAddressAddressLine1`, `EntityAddressCityOrTown`, `EntityAddressStateOrProvince`, `EntityAddressPostalZipCode`, `CityAreaCode`/`LocalPhoneNumber` — the exact same taxonomy family as `dei:EntityPublicFloat` (already mapped as `public_float`, `statements/classify.py`) and `dei:EntityTaxIdentificationNumber` (below). Same fetch cost as zero (already inside every company's already-fetched `companyfacts.json`), same curation pattern as `public_float`'s own addition. **Not verified live against the real database in this pass** — this task was scoped read-only, no DB access — so before committing build time, run the same live-count check doc 28 ran for R&D/interest income (`select count(*) from core.fact where concept ... dei:EntityAddressAddressLine1`) to confirm real coverage before assuming it generalizes across the full population the way it does for the single NVDA example here.

### 2. Employer ID (EIN) — confirms doc 30 Track 7 / doc 31, still not built
`dei:EntityTaxIdentificationNumber` (NVDA: 94-3177549). Checked in code: no reference anywhere in `company_master/`, `mapper/`, or the `core.company` migration files. Same cheap shape as `sic_code`/`public_float` — a standard, single cover-page `dei` tag, zero new fetch. Doc 31 already ranks this correctly; this pass simply reconfirms it's still genuinely open, not stale.

### 3. Widen `FORM_ALLOWLIST` for Form 144, 424B5, FWP — confirms doc 30 Track 7 / doc 31, still not built
Verified directly against the *current* `normalizer/identity.py`: `FORM_ALLOWLIST` now includes `10-K(/A)`, `10-Q(/A)`, `20-F(/A)`, `40-F(/A)`, `8-K(/A)`, the Form 15 family, `SC 14D9(/A)`, and the DEF 14A family — real growth since doc 30/31 were last updated, but **Form 144, 424B5, and FWP are still absent**. All three appear in NVDA's real "Latest SEC Filings" feed on the Profile page (Jun 15-22, 2026). Already sitting in `raw.sec_submissions` (Collector fetches every form type) — this remains a pure allowlist-widening task, zero new fetch, same additive pattern already used four times over (8-K → Form 15/SC 14D9 → DEF 14A family).

### 4. Net Cash (Cash − Debt) and Net Cash Per Share
Checked in code: `cash_and_equivalents` and `total_debt` are both already-mapped canonical concepts (used together today only inside `net_debt_ebitda`'s hardcoded Python, `mapper/expanded_metrics.py`). Confirmed no standalone `net_cash` or `net_cash_per_share` `metric_definition` row exists in `expanded_definitions.py`. A trivial `sum_diff` shape (same engine shape `fcf` already uses) plus a division by `shares_outstanding` — zero new concepts, zero new fetch. StockAnalysis's own Financials page tracks this as a first-class annual line (`Net Cash (Debt)`, `Net Cash Per Share`, both with growth %).

### 5. Pretax Margin
Checked in code: `income_before_tax` is already a resolved canonical concept (used today only as ROIC's `tax_rate_denominator`, `mapper/definitions.py`). No `pretax_margin` metric exists alongside the already-built `gross_margin`/`operating_margin`/`net_margin` trio. A one-line ratio addition (`income_before_tax / revenue`), same `FORMULA_SHAPES["ratio"]` engine path the other three margins already use — literally the cheapest possible new metric in this entire list.

### 6. Dividend Per Share YoY Growth Rate as its own metric
StockAnalysis's Financials page shows "Dividend Per Share Growth" as a first-class annual series (600.00% for NVDA's FY2026, reflecting a real split-adjusted step-up). Checked `mapper/ttm.py`'s `GROWTH_METRICS` dict directly: it has `revenue_growth_yoy/3y/5y/10y_cagr` and `eps_growth_yoy/3y/5y/10y_cagr`, but no `dividends_per_share`-based entry at all — despite `dividends_per_share` already being a resolved canonical concept and `_growth_value()` already being fully generic (doc 26's own 5Y/10Y CAGR addition needed zero new logic, just new dict keys). Adding `dividend_growth_yoy` (and optionally 3Y CAGR) is the single cheapest metric addition possible in this codebase today — one dict entry, reusing 100% existing code, the exact same shape as the 5Y/10Y CAGR work already done twice.

---

## 4. Repeats of existing gap-analysis findings — confirmed still open, not re-derived as new

- **Payout Ratio** (`dividends_paid / net_income`, or `dividends_per_share / diluted_eps`) — doc 26 §2 already named this as a zero-new-fetch derived metric. Checked in code: still not built (`payout_ratio` doesn't appear in `expanded_definitions.py`). Cheap, still open, no new evidence beyond doc 26's own.
- **Beta** — doc 28 already flagged this exact StockAnalysis-style standalone stat as a genuine gray area (fundamental-adjacent risk stat vs. "technical indicator" MVP exclusion), needing a founder call rather than an assumed yes/no. NVDA's page shows Beta as its own top-line stat (2.21), same framing doc 28 already anticipated. No new information this pass.
- **Segment/geography revenue and all "Operating Metrics & Breakdowns"** — doc 22/23/30 Track 7 already confirmed this needs dimensional XBRL (hard, company-specific) or a paid vendor. This pass adds one more confirming data point (Fiscal.ai named specifically for the *coarsest* segment cut on the Financials page, not just TipRanks for the granular Metrics-page breakdowns) but reaches the same conclusion.
- **Dividend Record/Pay Dates** — doc 30 Track 7 already flagged this as needing 8-K text parsing. This pass confirms the exact 4-column table shape rather than adding new scope.
- **52-Week Range, Forward PE, Analyst Price Target/Consensus, technical indicators** — all previously and repeatedly confirmed vendor-blocked (docs 22/26/28/30/31). No new evidence, no reason to revisit.

---

## 5. What's NOT recommended

Executive bios/roster and Company Description/Founded/CEO fields all trace to named third-party vendors (EOD Historical Data, S&P Global Market Intelligence) on StockAnalysis's own page — not a case of "EDGAR has this and we haven't parsed it yet." Building a from-scratch DEF 14A/10-K free-text parser to approximate these would be real, unstructured-text work (doc 19 Stage 5's deferred territory), not a cheap win, and StockAnalysis itself didn't attempt it either — it paid a vendor instead. CUSIP/ISIN at the company level aren't standard `dei` tags and have no clean EDGAR source; not worth a dedicated build for two fields with no screening or trust value beyond novelty.

---

## 6. Ranked summary — best zero/low-cost items to build next

1. **Cover-page `dei` cluster: Employer ID (EIN) + Address/Phone.** Same tag family as the already-proven `public_float` addition, same curation pattern, genuinely zero new fetch. The EIN half is already named by doc 31; the address/phone half is new to this pass. Do these together as one small `statements/classify.py`-style addition, but confirm live coverage (a `select count(*)` against the real `core.fact` table, same discipline as every prior concept addition in this project) before committing, since this pass had no DB access to check it directly.
2. **Net Cash / Net Cash Per Share.** Zero new concepts (both inputs already resolved), one new composite metric definition, mirrors `fcf`'s existing `sum_diff` shape exactly.
3. **Pretax Margin + Dividend Per Share YoY Growth.** Two separate one-line additions, both reusing 100% existing engine code paths (`FORMULA_SHAPES["ratio"]` and `GROWTH_METRICS` respectively) — arguably the cheapest two metrics this codebase could add, full stop.

Widening `FORM_ALLOWLIST` for Form 144/424B5/FWP and building Payout Ratio remain correctly ranked in docs 26/31 and aren't re-ranked here — they're confirmed still open, not deprioritized.

Nothing in this document is built. Every "already have" claim above was checked against the live code (file and line cited), not against a prior doc's own summary of that code — consistent with this project's stated concern that prior gap-analysis docs have gone stale relative to actual pipeline state.
