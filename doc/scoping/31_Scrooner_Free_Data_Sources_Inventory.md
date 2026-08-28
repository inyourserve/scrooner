# Doc 31 — Free Data Sources Inventory: What Exists, What We Use, What's Worth Scoping

**Status:** Draft (2026-08-27), **corrected 2026-08-28** · Owner: Founder/Product · Review: when a new source is added or an open item gets scoped

**Correction (2026-08-28):** this doc originally listed 8-K `items` and `dei:EntityPublicFloat` as the top-priority *unbuilt* items. A verification pass found both were already built and already run against the full population as of 2026-08-26 (`core.filing.items` populated by `normalizer/identity.py`, `dei:EntityPublicFloat` mapped as the `public_float` canonical concept in `statements/classify.py` — see `doc/planning/24_Scrooner_Final_Build_Backlog.md` lines 23/25 for the original completion evidence, including a real AAPL public_float value). This doc was simply stale relative to doc 24, not a build gap. Both rows below are corrected to reflect reality.

Prompted by an explicit ask: lay out every free/official data source relevant to Scrooner (not just SEC), what each actually provides, what's already built, and what's realistically worth doing next. Synthesizes prior gap-analysis work (docs 07, 18, 21, 22, 23, 26, 28, 30) rather than re-deriving it, and adds sources outside SEC that hadn't been inventoried together before.

---

## 1. SEC / EDGAR sources

### 1a. Already built and in production use

| Source | What it provides | Built in | Status |
|---|---|---|---|
| **`submissions.json` bulk zip** (per-CIK filing index) | Every filing a company has made: form type, accession number, filing/period dates, entity metadata (SIC, exchanges, former names) | `raw.sec_submissions`, Collector | ✅ Full population |
| **`companyfacts.json` bulk zip** (per-CIK XBRL facts) | Every XBRL-tagged financial fact a company has ever reported, all periods | `raw.sec_companyfacts`, Collector → Normalizer → Mapper | ✅ Full population |
| **Individual filing documents** (Form 4, Schedule 13D/13G XML/HTML bodies) | Actual transaction/ownership detail — not in the index, must be fetched per filing | `ownership/insider.py`, `ownership/beneficial_ownership.py` | 🔄 Golden-10 done; full-population expansion in progress (Track 2) |
| **Form 13F bulk data set** (quarterly, all managers) | Institutional holdings, matched to our companies via CUSIP crosswalk | `ownership/institutional.py` | ✅ Golden-10 (one recent window only — see gap below) |
| **XBRL Frames API** | Cross-company snapshot of one concept/period (used for coverage-gap checks, not ingestion) | Verification tooling only | ✅ Used for scoping, not a data pipeline |
| **8-K `items`** | SEC's structured event classification (earnings, M&A, exec changes, bylaw amendments, shareholder votes) | `core.filing.items`, parsed in `normalizer/identity.py` | ✅ Full population (corrected 2026-08-28 — was wrongly listed as unbuilt below) |
| **`dei:EntityPublicFloat`** | Real, vendor-independent market-cap proxy | `public_float` canonical concept, `statements/classify.py` | ✅ Full population (corrected 2026-08-28 — was wrongly listed as unbuilt below) |

### 1b. Real, scoped gaps — not yet built or only partially built

| Source/field | What it provides | Value | Fetch cost | Status |
|---|---|---|---|---|
| **Form 144** | Notice of a *proposed* insider sale — filed before the actual sale (Form 4 comes after) | Medium — earlier signal than Form 4 | Low (same per-filing-doc pattern as Form 4) | ⬜ Not built (doc 30 Track 7) |
| **Form 15** | Deregistration — the cleanest possible "going private/delisting" signal, form type alone is the whole signal | Medium | **None** (just widen `FORM_ALLOWLIST`) | ⬜ Not built (doc 23) |
| **SC 14D9 / SC TO** | Tender offer activity (M&A in progress), filed by the actual target, zero issuer ambiguity | Medium | Low (filing-presence only) | ⬜ Not built (doc 23) |
| **DEF 14A deep parsing** | Executive compensation tables, insider stock ownership tables, board composition — currently only filing *presence* is captured | High, but real unstructured-text-parsing project | High | ⬜ Deferred, P2 (doc 19 Stage 5) |
| **Form N-PORT** | Mutual fund portfolio holdings (a separate universe from 13F's institutional managers) | Medium — cleanly separates "fund ownership" from generic institutional | Medium (new bulk fetch, reuses existing CUSIP-match pattern) | ⬜ Not built (doc 21) |
| **Multi-quarter Form 13F** | Ownership *trend* over time — current data is one recent filing window only | Medium-high for a "smart money accumulating/distributing" signal | Medium-high (genuinely new historical bulk fetches, ~50K+ rows/quarter) | ⬜ Not built (doc 28) |
| **Dimensional/segment XBRL** (revenue by segment/geography) | Real investor-relevant breakdown, but company-specific custom XBRL extensions, not a universal schema | High value, confirmed genuinely hard | Very high — no clean mapping path exists | ⬜ Correctly left undesigned (doc 23) — competitors (TipRanks) source this from a paid vendor, not EDGAR |
| **424B5 / FWP / Form 144** as form-type additions | Prospectus supplements and free-writing prospectuses — capital-raise/dilution signal | Low-medium | **None** (just widen `FORM_ALLOWLIST`) | ⬜ Not built (doc 30 Track 7) |

### 1c. SEC bulk datasets not yet evaluated at all

| Source | What it provides | Worth checking? |
|---|---|---|
| **SEC DERA Financial Statement Data Sets** (quarterly `.tsv` bulk files, separate from `companyfacts`) | Every company's full financial-statement line items in structured, pre-parsed tabular form, refreshed quarterly | Possibly redundant with what `companyfacts`/Normalizer already gives us — worth a quick evaluation pass before investing, not an assumed win |
| **SEC full-text search index (EFTS)** | Keyword search across all filing text | Could power a "search filings for X" feature later; not a fundamentals data source |

---

## 2. Non-SEC free/official government sources

| Source | What it provides | Relevance to Scrooner | Status |
|---|---|---|---|
| **FRED (Federal Reserve Economic Data)** | Interest rates, Treasury yields, CPI, GDP, unemployment — free, no API key needed for basic use, generous rate limits | Real: risk-free rate for any DCF/valuation context, macro backdrop for a screen ("rates rising" context) | ⬜ Not used |
| **U.S. Treasury (treasurydirect.gov / fiscaldata.treasury.gov)** | Daily Treasury yield curve rates | Same use as FRED for risk-free rate; either source works | ⬜ Not used |
| **BLS (Bureau of Labor Statistics)** | CPI, employment, wage data | Lower relevance — more useful for macro commentary than per-company screening | ⬜ Not evaluated |
| **Census Bureau (Business Formation Statistics, economic indicators)** | Broad economic context | Low relevance to a fundamentals screener | ⬜ Not evaluated |
| **FDIC BankFind / call reports** | Bank-specific regulatory financials (capital ratios, etc.) | Could fill JPM/ARCC-style bank-specific metric gaps (doc 26 named financial-institution reporting as a real, structural gap for standard ratios) | ⬜ Not evaluated — real candidate for the "bank metrics don't fit the standard formula" problem |
| **USPTO (patent/trademark data)** | Patent filing counts, grants | A possible innovation-signal metric for tech companies; speculative, not validated demand | ⬜ Not evaluated, low priority |

---

## 3. Free-tier market-data platforms (not government, but free/cheap)

| Source | What it provides | Status |
|---|---|---|
| **Alpaca Markets** | Real EOD/delayed price data (`delayed_sip` feed) | ✅ Already integrated (`core.market_price_alpaca`), doc 25 |
| **OpenFIGI** | Security-type/ticker classification | ⚠️ Evaluated and **dropped** for full-population use (2026-08-23) — rate-limit cost wasn't worth it once SEC's own sector data proved sufficient |
| **Nasdaq Data Link (formerly Quandl) free datasets** | Assorted free tables (varies by dataset, many deprecated/paid-only now) | ⬜ Not evaluated — free tier has shrunk significantly over the years, needs a fresh check before assuming anything is still free |
| **IEX Cloud** | Real-time/historical price, fundamentals (mostly paid now) | ⬜ Not evaluated — largely moved to paid tiers; low priority given Alpaca is already working |

---

## 4. What's already done (summary, cross-referenced to source docs)

- Full SEC filing index + XBRL facts for the entire eligible US population (5,257+ companies) — Collector/Normalizer/Mapper, docs 08/09/11
- 18 locked V1 metrics + expanded metrics (Piotroski, quality flags, reconciliation, EBITDA-based ratios, dilution trend, etc.) — docs 11, 18, 26
- Company identity (SIC, ticker history, active/stale status) — doc 13
- Real market price via Alpaca — doc 25
- Form 4 insider transactions, Schedule 13D/13G beneficial ownership, Form 13F institutional holdings (golden-10 complete, full-population expansion in progress) — doc 19
- 8-K `items` + `dei:EntityPublicFloat` (corrected 2026-08-28 — already built and run against the full population, see section 1a)

## 5. What's realistically worth scoping next, in order

1. **Form 15, SC 14D9/TO, Form 144, 424B5/FWP** — cheap form-type/document additions that reuse existing fetch infrastructure once it's not busy with Track 2.
2. **FRED/Treasury yield data** — a genuinely new, non-SEC source, but simple (a handful of well-known series, no per-company fetch needed) — worth a small standalone build for a risk-free-rate input to any future valuation-context feature.
3. **FDIC bank-specific financials** — worth a real evaluation pass given it directly targets an already-named, real gap (bank-specific metrics for JPM/ARCC-style companies).
4. **DEF 14A parsing, Form N-PORT, multi-quarter 13F** — real value, but each is its own substantial project (unstructured text parsing, or genuinely new large bulk fetches). Scope these individually when there's dedicated time, not as an add-on to something else.
5. **SEC DERA Financial Statement Data Sets** — evaluate first (may be redundant with what we already extract from `companyfacts`) before treating it as a new source worth building against.

## 6. What's deliberately not being chased

- **Dimensional/segment XBRL** — confirmed genuinely hard (company-specific custom extensions, no universal schema); even paid vendors that offer this (TipRanks) don't source it from EDGAR.
- **Analyst estimates, price targets, short interest** — no free official source exists; explicitly out of MVP scope (doc 02).
- **Foreign private issuer (20-F/40-F) coverage** — resolved as out-of-scope for V1 (doc 02, closed 2026-08-27) — untested IFRS-vs-GAAP mapping risk, no demonstrated demand.
