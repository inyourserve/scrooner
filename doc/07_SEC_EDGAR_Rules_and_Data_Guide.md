# 07 — SEC EDGAR: Rules, Access, and Data Reference

A complete reference on how EDGAR works, what's legally and technically allowed when pulling from it, every API and bulk-data source available, and the form types Scrooner cares about. Written for whoever builds or reviews the Collector.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When SEC changes access rules, endpoints, or data formats

---

## 1. What EDGAR actually is

EDGAR — Electronic Data Gathering, Analysis, and Retrieval — is the SEC's system for accepting, indexing, and publishing the disclosure documents that public companies, insiders, and certain funds/investors are legally required to file. Filers (or their agents) submit through EDGAR under Regulation S-T (17 CFR Part 232); the SEC publishes what's filed essentially as-is. EDGAR is the filing system and the public archive — Scrooner is not going around some paywall or scraping a private aggregator, it's reading the same primary-source record that regulators, journalists, and every other financial data company reads.

Two separate systems matter here, and it's worth keeping them distinct:

- **EDGAR (filing side)** — how companies submit disclosures to the SEC. Recently overhauled under **EDGAR Next** (see §6).
- **EDGAR (data side)** — `www.sec.gov` and `data.sec.gov`, where the public reads what's been filed. This is everything Scrooner's Collector touches.

---

## 2. The legal backdrop, briefly

- **Securities Act of 1933** and **Securities Exchange Act of 1934** are why most of this data exists at all — they require periodic and event-driven disclosure from public companies.
- **Regulation S-K** sets what has to be disclosed (financial statements, risk factors, executive comp, etc.) and in what filings.
- **Regulation S-T** governs electronic submission through EDGAR.
- **XBRL / Inline XBRL mandate** — the SEC phased in structured, machine-readable tagging of financial statements starting in the early 2010s (large accelerated filers first), moving to **Inline XBRL (iXBRL)** as the required format by 2018–2021 depending on filer size. This is *why* a Normalizer/Mapper pipeline is even possible — before this mandate, "parsing" a filing meant scraping HTML/PDF prose, not reading tagged facts.
- **dei (Document and Entity Information) taxonomy** — a companion taxonomy alongside us-gaap that tags entity-level facts (fiscal year end, entity name, shares outstanding, filer category) rather than financial-statement line items. Scrooner's Mapper will touch both taxonomies, not just us-gaap.

None of this needs to become Scrooner product copy, but it's the "why" behind several locked decisions in doc 02 (XBRL-based normalization, US-listed-only for V1, deterministic mapping).

---

## 3. Access rules — what's actually allowed

This is the part the Collector must get right, because getting it wrong risks a block, not just a failed request.

### Rate limit

**Maximum 10 requests per second**, enforced per source/IP. The SEC explicitly reserves the right to throttle further "to preserve equitable access for all users," and does not provide technical support for scripts that get rate-limited or blocked.

> Doc 02's locked decision — *"keep the aggregate internal request rate at or below 8 requests per second"* — is a deliberate buffer under this 10/sec ceiling, not a misreading of it. Keep that buffer; don't creep toward 10/sec just because it's technically allowed.

### Required header

Every request must declare a `User-Agent` identifying who's making it — SEC's own example format:

```
User-Agent: Sample Company Name AdminContact@yourdomain.com
Accept-Encoding: gzip, deflate
Host: www.sec.gov
```

A generic or missing User-Agent is the single most common cause of a 403 from `data.sec.gov` / `www.sec.gov`. This should be a hard-coded, never-forgotten header on every Collector request.

### Fair-access expectations (not just rate limits)

- "Use efficient scripting. Download only what you need and please moderate requests to minimize server load." — i.e. prefer the targeted JSON APIs and bulk ZIPs over re-crawling HTML pages.
- Botnets and automated tools operating outside the stated policy are explicitly called out as being managed/blocked.
- No CORS support on `data.sec.gov` — irrelevant for a server-side Python Collector, relevant if anyone's ever tempted to call these APIs directly from a browser.

### Practical Collector implications

- Hard rate-limit the Collector well under 10 req/sec (doc 02's 8/sec stands).
- Set the User-Agent from a config value, not hardcoded per-script, so it survives a founder-name or domain change.
- Prefer bulk ZIPs (§5) for full-universe backfills over hammering the per-company JSON endpoints thousands of times.
- Respect `Retry-After`/backoff on 429s; don't treat a rate-limit response as a hard failure to alert on immediately — retry with backoff first (this is exactly what doc 02's Tenacity-based retry logic is for).

---

## 4. The APIs (`data.sec.gov`)

All of the following are unauthenticated, JSON, no API key required — just the User-Agent header and rate-limit discipline above.

### Submissions API

```
https://data.sec.gov/submissions/CIK##########.json
```

Filing history and identity metadata for one company: current and former names, tickers, exchanges, SIC code, and at least a year (or 1,000 filings) of recent filing history in a columnar format. Updates in near real time (sub-second typical delay after a new filing hits EDGAR).

### XBRL Company Concept API

```
https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/{ConceptName}.json
```

All disclosed values for one company, one taxonomy tag (e.g. `Revenues`, `NetIncomeLoss`), across every period reported, split out by unit (USD vs. shares vs. other).

### XBRL Company Facts API

```
https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
```

Everything the Company Concept API returns, for every tag the company has ever reported, in one call — the practical default for "give me all this company's structured financial data."

### XBRL Frames API

```
https://data.sec.gov/api/xbrl/frames/us-gaap/{Concept}/{Unit}/{Period}.json
```

The inverse query: one fact, one period, across *every* company that reported it. Period format: `CY2024` (annual), `CY2024Q1` (quarterly), `CY2024Q1I` (instantaneous/point-in-time, e.g. balance-sheet items). Useful for cross-sectional screens and for validating the Mapper against a whole cohort at once, not just one golden company.

### EDGAR Full-Text Search API

```
https://efts.sec.gov/LATEST/search-index?q={query}&forms={formTypes}&dateRange=custom&startdt=YYYY-MM-DD&enddt=YYYY-MM-DD&from={offset}&size={pageSize}
```

Full-text search across all EDGAR filings submitted since **2001**. `size` maxes out at 100 per page. This is the one API that searches filing *prose*, not structured facts — useful later for things like flagging "material weakness" mentions, but out of scope for the deterministic Collector/Normalizer/Mapper pipeline per doc 02/03 (no news/sentiment/text-mining in MVP).

---

## 5. Bulk data (for full-universe backfill, not per-company polling)

| Resource | URL | Contents |
|---|---|---|
| Ticker → CIK map | `https://www.sec.gov/files/company_tickers.json` | Ticker/CIK/company-name associations, the same data that powers EDGAR's own search typeahead |
| Ticker → CIK (legacy flat file) | `https://www.sec.gov/include/ticker.txt` | Tab-delimited ticker-to-CIK mapping |
| Full CIK lookup (all filers, not just tickered) | `cik-lookup-data.txt` (linked from SEC's company search tools) | Broader than company_tickers.json — includes filers without a public ticker (funds, insiders, etc.) |
| All company facts, bulk | `https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip` | Every company's XBRL Company Facts API output, recompiled **nightly**, in one archive — the efficient way to bootstrap instead of one HTTP call per CIK |
| All submissions, bulk | `https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip` | Every company's Submissions API output, recompiled **nightly** |
| Daily index | `https://www.sec.gov/Archives/edgar/daily-index/` | What was filed on a given day — the incremental-update source once bootstrap is done |
| Full (quarterly) index | `https://www.sec.gov/Archives/edgar/full-index/` | `form.idx`, `company.idx`, `master.idx`/`.json` per quarter — a rolling index from quarter-start to the previous business day |
| Financial Statement Data Sets (DERA) | `https://www.sec.gov/about/dera_financial-statement-data-set` | SEC's Division of Economic and Risk Analysis publishes flattened, **quarterly** extracts of financial-statement XBRL data (`num.txt`, `sub.txt`, `tag.txt`, etc.) — more compact than companyfacts.zip, doesn't carry all metadata, but easy to bulk-load into a relational shape. Worth evaluating as a second-opinion cross-check for the Mapper, not necessarily a primary source (it lags — quarterly, vs. companyfacts.zip nightly). |
| Financial Statement *and Notes* Data Sets | `https://www.sec.gov/about/dera_financialstatementandnotesdatasets` | A deeper DERA extract that also covers footnote-level tagged disclosures, not just face-of-statement numbers — likely out of scope for MVP's ~15–20 metrics, but useful later if Scrooner ever needs footnote-level detail |

**Bootstrap strategy implied by this table** (matches doc 02/04's "bootstrap with bulk archives, incremental via daily indexes"): pull `companyfacts.zip` + `submissions.zip` once to seed the whole universe, then poll the **daily index** going forward for what's new, falling back to the per-company JSON APIs only for spot-checks, golden-company reconciliation, or a company that's missing/stale in the nightly bulk file.

---

## 6. EDGAR Next — does it affect Scrooner?

**No, not for data consumption.** EDGAR Next (mandatory as of the 2025 compliance deadline) changes how *filers* authenticate and manage access to submit filings — Login.gov credentials, multifactor auth, role-based account permissions. It has **no effect on reading public EDGAR data** via the APIs or bulk files above; those remain open, unauthenticated, and governed only by the fair-access rules in §3. Flagging this mainly so nobody on the team burns time worrying about it — it's a filer-side change, and Scrooner is never a filer.

---

## 7. Data licensing — can Scrooner actually redistribute this?

Yes. SEC filings and the data derived from them by the SEC itself are **U.S. government works and public domain** — not copyrighted, free to use, reproduce, and redistribute, including commercially. This is the entire premise behind Scrooner's "no data-cost trap" moat from doc 01: EDGAR data is free and legally Scrooner's to keep republishing forever.

A few things worth being precise about, though:

- **Public domain applies to the SEC's own filed data**, not automatically to any third-party content that happens to be embedded in a filing (e.g. a photo, or content a company licensed from someone else and included as an exhibit). This basically never matters for financial statement numbers, but worth remembering if the pipeline ever touches filing exhibits/attachments more broadly.
- **The SEC provides no warranty of accuracy** for EDGAR data and offers no technical support for third-party integrations. This is exactly why doc 05's data-quality methodology (golden-company reconciliation, lineage tests, confidence states) exists — the SEC is the authoritative *source*, not a guarantee of correctness once it's flowed through Scrooner's own pipeline. Scrooner's trust moat has to be earned on top of EDGAR, not assumed from it.
- **"Not investment advice" and similar disclaimers are Scrooner's obligation, not something EDGAR licensing handles for the product.** This ties to the open decision in doc 02 ("legal disclaimers and data licensing review" — due before public launch) — that's about how Scrooner presents and disclaims its *own* derived output, not about whether the underlying EDGAR data can be used (it can).

---

## 8. Form types Scrooner's Collector needs to know about

Not exhaustive — EDGAR has hundreds of form types — but this is the practical set for a US-listed-equities fundamental screener.

| Form | What it is | Why Scrooner cares |
|---|---|---|
| **10-K** | Annual report | Primary source for full-year financials, MD&A, risk factors — the backbone of most metrics |
| **10-K/A** | Amended annual report | Restatements — must supersede, not duplicate, the original in the Mapper |
| **10-Q** | Quarterly report | Quarterly financials for trailing-twelve-month and quarter-over-quarter metrics |
| **10-Q/A** | Amended quarterly report | Same amendment-handling requirement as 10-K/A |
| **8-K** | Current report (material events) | Earnings releases often arrive here (via Item 2.02 exhibit) before the 10-Q/10-K — a potential *early* data source, but unstructured/semi-structured, so lower priority than XBRL-tagged periodic reports for MVP |
| **20-F** | Annual report for foreign private issuers | Non-US-domiciled companies listed on US exchanges — explicitly excluded from MVP scope per doc 03 ("non-US exchanges" excluded), but 20-F filers can still be US-*listed*, so this is a boundary case worth an explicit product decision, not an assumption |
| **40-F** | Annual report for certain Canadian issuers (MJDS) | Same boundary-case note as 20-F |
| **S-1 / S-1/A** | IPO registration statement | Not periodic financials in the same structured sense; relevant later for newly-public companies, not core to MVP |
| **DEF 14A** | Definitive proxy statement | Executive compensation, board composition, shareholder votes — not in MVP's ~15–20 metric set, but the canonical source if/when Scrooner adds governance data |
| **Form 3 / 4 / 5** | Insider ownership — initial, changes, annual | Officer/director/10%-owner transactions — explicitly out of MVP scope (no insider-trading data in the current metric set), but worth knowing these exist under Section 16 of the Exchange Act |
| **Schedule 13D / 13G** | Beneficial ownership reporting (>5% stake) | Activist/large-holder disclosures under Exchange Act Sections 13(d)/(g) — same "exists, not in MVP" status as Forms 3/4/5 |
| **Form 13F (13F-HR / 13F-NT)** | Institutional investment manager holdings (HR = holdings report, NT = notice, filer relies on another's filing) | Quarterly holdings disclosure for large institutional managers — a possible future data product, not MVP. **Verified live 2026-08-14 (Day 5): appears for tracked equity issuers, not just funds** — JPMorgan Chase, GSK, ING Groep, Sumitomo Mitsui, Devon Energy, NetEase, Affiliated Managers Group and others in `raw.company_universe` file 13F-HR/13F-NT because banks, insurers, and diversified financials are frequently *also* institutional investment managers under a separate Exchange Act obligation — filing both as an issuer (10-K/10-Q) and as a manager (13F) is normal, not a sign the Collector's scope has leaked into funds. |
| **N-PX** | Fund/manager proxy voting record | Required for funds and (since a 2022 SEC rule change) 13F filers too — same dual-filer-capacity note as Form 13F above. Verified live: Ames National Corp and Hennessy Advisors, both tracked equities, file it. |
| **6-K** | Foreign private issuer current report | The 20-F filer's equivalent of an 8-K |
| **424B2 / 424B3 / 424B4 / 424B5** | Prospectus filed under Rule 424(b), variants by offering type | Securities-offering paperwork, not periodic financials — not in MVP scope, but the single most common form type observed in real daily-index data (Day 5: 251 of 559 sampled rows), so worth recognizing on sight |
| **144 / 144/A** | Notice of proposed sale of restricted/control securities (+ amendment) | Insider-adjacent disclosure, same "exists, not in MVP" status as Forms 3/4/5 |
| **FWP** | Free writing prospectus | Supplementary offering communication, not periodic financials |
| **425** | Prospectus/communication re: business combination | M&A-related filing, not periodic financials |
| **NT 10-Q / NT 10-K** | Notification of late filing | Signals a company missed its periodic-report deadline — a real, useful **data-freshness signal** (a tracked company that should have a new 10-Q but instead has an NT 10-Q on file isn't stale data, it's SEC-acknowledged lateness) worth keeping in mind for the freshness-checks/data-quality work in doc 05, even though it's not itself a financial statement |
| **DEFA14A** | Additional definitive proxy soliciting material | Companion to DEF 14A, same "exists, not in MVP" status |
| **EFFECT** | Notice of registration statement effectiveness | Administrative, not periodic financials |
| **ARS** | Annual report to security holders | Distinct from the 10-K despite the name — a shareholder-facing document, not the primary financial-statement source |
| **POS EX** | Post-effective amendment, exhibit only | Administrative, not periodic financials |

**All of the above (except 10-K/10-Q/20-F/40-F) were confirmed via real daily-index data pulled in Day 5** (`doc/learnings/day-05-incremental-updates.md`), not assumed — 26 distinct form types appeared in a two-day sample of just the 10 golden companies' filing activity, more than half of which weren't in this table before that check.

**MVP-relevant subset, per doc 03's "in scope" table:** effectively just **10-K, 10-Q, 20-F, 40-F** (for identity/coverage purposes) plus their amendments — the periodic, XBRL-tagged financial reports the Normalizer and Mapper actually need. Everything else in this table exists so the team recognizes it when it shows up in a company's filing history and doesn't accidentally try to parse it as a financial statement — the Collector itself doesn't filter by form type at all (doc 06 module 5 records everything a tracked company files), so all of this legitimately lands in `raw.sec_filing_documents`.

---

## 9. Company identity — CIK vs. ticker, again

Doc 06 already establishes CIK as the canonical identity and ticker as a mutable nickname; this section is the EDGAR-specific "why," for reference:

- A **CIK (Central Index Key)** is assigned once per filer and never reused or changed, even through ticker changes, relistings, or company renames.
- A **ticker** can change (rebrand, merger, exchange move), can be reused years later by a completely different company, and — for foreign issuers or certain filers — may not exist on EDGAR at all.
- `company_tickers.json` and `ticker.txt` are both *derived* convenience mappings maintained by the SEC on top of the CIK system, not the source of truth themselves.
- Filing URLs use a related but distinct identifier, the **accession number** (format `##########-YY-######`), unique per individual filing — the Collector's Filing Metadata module (doc 06) should key on accession number, not just CIK + date, to avoid ambiguity when a company files multiple documents close together.

---

## 10. Summary checklist for the Collector build

- [ ] User-Agent header hardcoded from config, present on every request, in SEC's recommended format
- [ ] Aggregate request rate capped at ≤8 req/sec (doc 02), safely under SEC's 10 req/sec ceiling
- [ ] Bootstrap via `companyfacts.zip` + `submissions.zip`, not per-company API calls, for the initial full-universe load
- [ ] Incremental updates via the daily index, not by re-pulling the full bulk ZIPs every run
- [ ] Retry/backoff (not immediate alarm) on 429/5xx responses
- [ ] CIK treated as the only stable identity; ticker/company_tickers.json treated as a derived, mutable convenience mapping
- [ ] Accession number used as the unique key for individual filings, not (CIK + date) alone
- [ ] Form-type awareness matches doc 03's MVP scope — 10-K/10-Q (+amendments) as the core source; everything else (8-K, DEF 14A, Forms 3/4/5, 13D/G, 13F, S-1) recognized but explicitly not parsed as financial data in MVP
- [ ] No assumption that EDGAR data is accuracy-guaranteed — golden-company reconciliation (doc 05) is what actually earns Scrooner's trust, not the source alone
