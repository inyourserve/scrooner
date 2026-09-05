# 22 — Scrooner: Full SEC EDGAR Surface Evaluation

Prompted directly: "evaluate all the SEC EDGAR API and their field, all the report and their field and use cases, and that can match our requirement or improve our screener... help users decide to invest or trade." **Extends doc 07, doesn't replace it** — doc 07 stays canonical for API mechanics/access rules/form-type inventory; this doc's job is the evaluation layer doc 07 was never meant to carry: what's actually used vs. unused, what's real but sitting idle in already-fetched data, and a ranked recommendation. Several findings below are new, checked live this pass, not restated from doc 07.

> **Status:** Draft (2026-08-17) — evaluation and recommendation, not a build plan or a decision. **Owner:** Founder / Product · **Review:** before anything below is built, and whenever doc 07 changes.

---

## 1. Data-delivery APIs — what's used, what's sitting idle

| API | Real fields (checked live) | Current use | Evaluation |
|---|---|---|---|
| **Submissions** (`data.sec.gov/submissions/CIK##.json`) | Beyond what's already used (name/tickers/filings): `ein`, `lei`, `category` (filer size class, e.g. "Large accelerated filer"), `insiderTransactionForIssuerExists`/`ForOwnerExists` (booleans), `flags` | Identity, filing list, `items` (8-K classification, doc 21) | `category` is already stored (`core.company.filer_category`, Company Master 4a). `ein`/`lei` are unused — `lei` in particular is a real, standard cross-dataset key (see §4, N-PORT/13F use CUSIP not LEI, so this is lower priority than it first looks, but worth keeping in mind if a future data source keys on LEI instead). `insiderTransactionForIssuerExists=0` would let `ownership/insider.py` skip a company entirely with zero fetches instead of discovering "no Form 4s" the expensive way — a real, small efficiency, not a correctness gap. |
| **Company Concept** (`.../companyconcept/CIK##/{taxonomy}/{tag}.json`) | One tag, one company, every period | Not used directly — `companyfacts` (below) is used instead, which is a superset | No gap. Company Concept is a narrower, redundant subset of what `companyfacts` already returns. Genuinely useful only for a targeted single-tag spot-check (e.g. manual debugging), not a pipeline data source. |
| **Company Facts** (`.../companyfacts/CIK##.json`) | Every tag, every taxonomy (`us-gaap`, `dei`, `ifrs-full`, `srt`), all periods, non-dimensional totals only | Core Normalizer source | **Confirmed live this pass: the API strips dimensional (segment/geography) breakdowns** — AAPL's `RevenueFromContractWithCustomerExcludingAssessedTax` via this API returns only the consolidated total, never the iPhone/Services/Mac split or Americas/Europe/China split a company's own 10-K reports. This is the real, confirmed shape of the "dimensional XBRL gap" doc 19 already flagged for segment revenue — it's an API limitation, not a Normalizer oversight; getting segment data needs a different source (the company's own XBRL instance document / R##.htm exhibits), a materially bigger parsing project than anything built so far. |
| **Frames** (`.../frames/us-gaap/{tag}/{unit}/{period}.json`) | One tag, one period, every company that reported it | Referenced for `concept_mapping` scaling evidence (doc 11 — 4 tags cover 3,000+ companies), not used as a live pipeline data source | Real, proven-useful for validation/coverage analysis. Not currently wired into any recurring job — worth keeping in mind if/when Scrooner screens a wider universe than the golden-10, since it's the only API that answers "who reported X this period" in one call instead of iterating companies. |
| **Full-Text Search** (`efts.sec.gov/LATEST/search-index`) | Prose search across all filings since 2001, `forms`/date-range filters, max 100 results/page | Not used (doc 07 already scopes this out for MVP — "no news/sentiment/text-mining") | Correctly out of scope for the deterministic core product. The one place it could matter later without violating doc 02's "AI is assistive only, never the source of financial truth": a **deterministic keyword flag** (not sentiment, not summarization) — e.g. "this 10-K contains the phrase 'material weakness'" as a boolean Pro/Con checklist item, same discipline as `prosCons.ts`'s existing deterministic bullets. Not proposed for building here, just noted as the one text-search use case that wouldn't cross doc 02's AI boundary. |

---

## 2. Bulk data sets — extending doc 07 §5

| Data set | Status | Evaluation |
|---|---|---|
| `companyfacts.zip` / `submissions.zip` | Used (Collector bootstrap) | — |
| Form 13F Data Sets | Used (Ownership Stage 4) | — |
| **Form N-PORT Data Sets** | **Built 2026-08-28/29** (superseding "scoped, not built" — see doc 21's correction note and `doc/reference/36_Scrooner_SEC_Filing_Types_Reference.md`) | `ownership/mutual_fund.py` + `ownership/mutual_fund_summary.py`, two consecutive quarterly windows, CUSIP-matched, verified against AAPL/MSFT (golden-10 only; full-population blocked on the beneficial-ownership CUSIP crosswalk finishing its own full-population expansion). |
| Financial Statement Data Sets (DERA) | Documented in doc 07, not used | Filing-oriented (one row per fact per filer per quarter, all companies), vs. `companyfacts.zip`'s per-company/all-history shape. Genuinely redundant with what the Normalizer already does better (full history, not quarterly snapshots) — no new evaluation needed, doc 07's existing "second-opinion cross-check, not primary source" verdict still holds. |
| Financial Statement *and Notes* Data Sets | Documented in doc 07, not used | Footnote-level tagged disclosure. Still out of scope — nothing in doc 02's locked metric list or doc 18's Tier A/B needs footnote-level granularity. |
| **Form N-CEN Data Sets** (annual fund census) | Not in doc 07, checked this pass | Fund-*level* administrative data (fund identity, adviser, service providers) — not security-level holdings. No use case for a stock screener; skip. |
| **Form N-MFP Data Sets** (money-market fund portfolio) | Not in doc 07, checked this pass | Money-market fund holdings specifically — out of scope by construction (Scrooner doesn't cover money-market instruments). Skip. |

---

## 3. Form types — additions to doc 07 §8's 26-form table

Doc 07's table is comprehensive for what Scrooner's Collector actually encounters in real daily-index data. A few real, relevant form types weren't in that sample and are worth adding for completeness of this evaluation:

| Form | What it is | Fit for "help a user decide to invest/trade" |
|---|---|---|
| **Form 15** | Notice of termination/suspension of registration (deregistration) | **Directly fixes a known, named gap**: root `CLAUDE.md` already flags that Company Master's `status` column can't represent `delisted` — "this project has no data source to confirm it." Form 15 *is* that data source. A company with a Form 15 on file has formally told the SEC it's going private/deregistering — a real, structured, unambiguous signal, not an inference. |
| **SC TO-T / SC TO-I** (tender offer, third-party / issuer) | Tender offer commencement documents | Real-time M&A signal, structurally similar to Schedule 13D's cover-page shape (likely has a subject-company CIK/CUSIP the same way 13D/G does — not yet verified live, would need the same issuer-vs-filer check pattern as doc 19's other schedules before trusting it). Directly investor-relevant: "someone is trying to buy this company" is about as decision-relevant as a signal gets. |
| **Form D** | Notice of exempt private-placement offering (Reg D) | Low fit — this is what private/pre-IPO companies file, not Scrooner's already-public universe. Skip. |
| **11-K** | Annual report for employee stock purchase/benefit plans | Low fit — administrative, not a company-performance or ownership signal an investor screens on. Skip. |

---

## 4. Structured fields already fetched, currently unused — the real find of this pass

These aren't new APIs or new form types — they're **fields inside documents this project already downloads**, unused because nobody had looked for them yet. Checked live, not assumed, matching this project's own standing discipline (doc 05).

- **`dei:EntityPublicFloat`** — every 10-K discloses this on its cover page: the market value of shares held by non-affiliates, as of the last business day of the filer's second fiscal quarter. Confirmed live for AAPL: **$3.253 trillion as of 2025-03-28** — a real, plausible, already-normalized fact sitting in `core.fact`, completely unmapped to any `analytics.canonical_concept`. This is not a substitute for a real market-price feed (it's annual, excludes insider-held shares, and lags by design) — but it's a **free, already-in-hand, directionally-real market-cap proxy**, available *today*, with zero dependency on doc 02's still-open price-vendor decision. Worth a real "is this good enough to unblock a rough Market Cap display" conversation rather than leaving it unmapped by default.
- **`dei:EntityCommonStockSharesOutstanding`** — already mapped (`shares_outstanding`, confirmed live), quarterly-updated, real value for AAPL: 14.59B shares as of 2026-07-17, trending down consistently with known buyback activity. Already captured; worth confirming it's actually surfaced somewhere (dilution-trend metric, doc 18 Tier A's "Share Count Dilution Trend" candidate) rather than mapped-but-dormant.
- **Form 4's `aff10b5One` field** — confirmed live in a real, already-fetched AAPL Form 4 XML (the exact document `ownership/insider.py` already downloads and parses): `<aff10b5One>false</aff10b5One>`, the SEC's 2023 rule addition disclosing whether a transaction was executed under a pre-arranged Rule 10b5-1 trading plan. **This is a real signal-quality field for the insider-activity feed that's already the product's own named differentiator (doc 10)** — a scheduled 10b5-1 sale is a much weaker "this insider is bearish" signal than a discretionary one, and right now the company page can't distinguish them. Zero new fetch — it's in the document already being parsed, just not captured into `core.insider_transaction`.

---

## 5. Prioritized recommendation

Ranked by real investor decision-value per unit of build effort, not by novelty:

1. **Capture 8-K `items` on `core.filing`** (doc 21, already scoped) — still the single highest-leverage item across both this doc and doc 21: zero new fetches, SEC's own structured classification, unlocks a real corporate-actions feed.
2. **Capture Form 4's `aff10b5One`** (new finding, this doc) — zero new fetch, same document already parsed, directly strengthens the Ownership & Insider Activity feature doc 10 named as the actual premium differentiator. Cheapest real improvement in this entire evaluation.
3. **Map `dei:EntityPublicFloat` as a rough, honestly-labeled Market Cap proxy** (new finding, this doc) — zero new fetch, already-normalized data, would be the first real (if imperfect) number in the company page's currently-null Market Cap field, without waiting on doc 02's price-vendor decision. Needs an explicit product call on how to label its imprecision (annual, excludes insiders) — a decision, not just a build task.
4. **Form N-PORT for mutual-fund-only ownership** (doc 21, already scoped) — real value, bigger effort (new bulk-data ingestion, ~420MB/quarter) than items 1-3. **Built 2026-08-28/29** — see doc 21's correction note.
5. **Form 15 → real `delisted` status** — fixes a named, standing gap (root `CLAUDE.md`'s own flagged limitation), low-effort once prioritized, but needs a live check of Form 15's own structure before treating it as done (not yet done this pass).
6. **Dimensional/segment XBRL (revenue by product/geography)** — confirmed real and confirmed genuinely bigger effort (the standard Company Facts API doesn't carry it at all — needs the company's own XBRL instance/exhibit parsing). Correctly still gated behind its own design pass, as doc 19 already said.
7. **SC TO-T/TO-I tender-offer tracking** — real M&A signal, not yet live-verified for structure (unlike everything else in this list, which was checked live this pass) — would need its own investigation before scoping further.

---

## 6. What this doc does not do

Same discipline as doc 18/19/20/21: no metric, field, or data source here is added to doc 02's locked list, and nothing above is built. This is the evaluation and ranking the user asked for, before any building starts.
