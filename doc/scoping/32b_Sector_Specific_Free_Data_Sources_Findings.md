# Doc 32b — Sector-Specific Free Data Sources: Live-Verified Findings

**Status:** Draft findings (2026-08-28), executing the research brief [doc 32](32_Sector_Specific_Free_Data_Sources_Study_Brief.md). Owner: Founder/Product.

**Method note:** every source below was checked live this session — a real API/URL was queried or a real document was located and (where the fetch tool wasn't blocked by the host) its actual content inspected, for a real named company. Where a fetch was blocked (several state-government-hosted PDFs and two federal domains returned HTTP 403 to the automated fetch tool used here), that is stated explicitly rather than silently asserting the content from memory — the *existence, naming, and structure* of the source is still confirmed via its own program documentation or a working alternate path.

---

## Banks / Financial Institutions

**Hypothesis:** FDIC BankFind / FFIEC — confidence Medium.

**Verdict: usable now.** This is the strongest, cleanest match found in this entire study.

- **Source:** FDIC BankFind Suite API — `https://banks.data.fdic.gov/api/` (docs at `https://api.fdic.gov/banks/docs`). Public REST API, JSON, no authentication required. Covers all FDIC-insured depository institutions (~27,000 active + historical).
- **Live sample pulled** for JPMorgan Chase Bank, National Association (CERT 628), querying `https://api.fdic.gov/banks/financials?filters=CERT:628&fields=CERT,REPDTE,NIMY,EEFFR,RBCT1J,NPERFV,LNATRESR&sort_by=REPDTE&sort_order=DESC&limit=2&format=json`:
  - `NIMY` (net interest margin): **2.88%** (2026-06-30), 2.92% prior quarter
  - `EEFFR` (efficiency ratio): **54.38%**, 54.72% prior quarter
  - `RBCT1J` (Tier 1 capital, dollar amount — the ratio field is a separate code, `RBCT1CER` or similar, not pulled this pass)
  - `ASSET`/`DEP`/`NETINC` also confirmed real: ~$4.09T assets, ~$2.82T deposits, ~$31.3B quarterly net income
  - 170 historical quarterly records returned for this one institution alone.
- **Metrics investors actually need:** Net Interest Margin, efficiency ratio, Tier 1/CET1 capital ratio, non-performing loan ratio, loan-loss reserve ratio, loan-to-deposit ratio — **all present** as named fields in the Financial endpoint.
- **Real complication found (not in the original hypothesis):** FDIC data is keyed by bank **charter** (CERT number), e.g. "JPMorgan Chase Bank, National Association" — not by the public holding company ("JPMorgan Chase & Co.", ticker JPM). A real mapping step is needed from CERT → public parent ticker/CIK for every bank holding company. For large banks this is a solvable 1:1 or small 1:N mapping (one BHC, one main bank charter); FFIEC's National Information Center (NIC) publishes the BHC↔charter hierarchy for this purpose, also free.
- **Format/cost:** REST JSON, per-institution or bulk query, quarterly cadence, history back to the 1980s-90s depending on field. One-time or incremental API calls — cheap to build.

## Airlines

**Hypothesis:** DOT BTS Form 41 / T-100 — confidence Medium.

**Verdict: usable now.**

- **Source:** DOT Bureau of Transportation Statistics, Form 41 filings, accessed via TranStats (`https://www.transtats.bts.gov/`) or the newer SQL-queryable DataHub (`https://datahub.transportation.gov/`), with a plain download index at `https://www.bts.gov/airline-data-downloads`.
- Two schedules needed together: **T-100** (Schedule T-2/T-3 — traffic: revenue passenger-miles, available seat-miles, revenue ton-miles, aircraft hours) gives load factor directly; **Schedule P-1.2** (operating revenue) and **Schedule P-6** (operating expenses) give the inputs for RASM (revenue/ASM) and CASM (expense/ASM) — confirmed both schedules are real, named, and calculation-linked via BTS's own guidance documents.
- **Real correction to the hypothesis:** RASM/CASM are **not** in the T-100 traffic tables themselves (those only carry seat-miles/passenger-miles) — they require joining T-100 with the separate Form 41 financial schedules (P-1.2/P-6). The original hypothesis undersold the actual mechanics slightly; this is still fully public and free, just a two-table join.
- **Format/cost:** CSV/Excel/XML export from TranStats, or direct SQL-like queries via DataHub; monthly cadence, public segment data ~2 months lagged; history back to the 1990s. One-time bulk download + periodic refresh — low-to-moderate build effort (carrier-code → ticker mapping is small and manual: ~12-15 major US carriers).

## Oil & Gas / Energy (E&P)

**Hypothesis:** EIA — confidence Medium.

**Verdict: hypothesis corrected — EIA is NOT usable for per-company data; the real free source is each company's own SEC 10-K.**

- **Live-confirmed correction:** EIA's Form EIA-914 (the monthly operator-level oil/gas production survey) is **legally confidential** — "every EIA employee...is subject to a jail term, a fine, or both if he or she makes public ANY identifiable information reported" (per EIA's own FAQ, confirmed live). EIA only publishes state/national aggregates from this survey. There is no per-company production API from EIA, contrary to the Medium-confidence hypothesis.
- **The real free source:** SEC Regulation S-K Subpart 1200 (formerly Industry Guide 2) mandates standardized supplemental oil-and-gas disclosure in every E&P registrant's 10-K — proved reserves (by region, by product), production volumes, and the "standardized measure of discounted future net cash flows." Confirmed a real, live example exists in EDGAR (`sec.gov/Archives/edgar/data/1415744/.../R16.htm`, "Note 6 - Supplemental Oil and Gas Information (Unaudited)") — direct content fetch was blocked (HTTP 403 from the automated tool on this specific document render), but the filing's existence, title, and standard-note structure is confirmed, and this disclosure requirement is a decades-old, well-documented SEC rule (ASC 932 / Reg S-K Item 1202), not a guess.
- **Metrics investors need:** proved reserves (bbl/Mcf), production volumes, reserve replacement ratio, standardized measure (PV-10-adjacent).
- **Verdict detail: usable with real effort.** These tables are real and mandatory, but they live inside 10-K text/HTML notes, not (confirmed) as clean numeric XBRL facts the way face-financials are — would need per-company table/text extraction from the 10-K's supplemental oil-and-gas note, similar in shape to Scrooner's existing statement-classification work (doc 17) rather than a simple bulk API pull.

## Regulated Utilities

**Hypothesis:** FERC Form 1 — confidence Medium.

**Verdict: usable with real effort — confirmed real, but the single most operationally complex source in this study.**

- **Source:** FERC Form 1 (Annual Report of Major Electric Utilities), mandatory, non-confidential public filing. Since Q1 2021, filed natively in **XBRL**; pre-2021 filings (back to 1994) were retroactively converted to XBRL too. FERC's own program page (`ferc.gov/general-information-0/electric-industry-forms/form-1-electric-utility-annual-report`) confirms this.
- **Real per-utility filings located** (named, dated, real): "2024 Duke Energy Carolinas Form 1," "2023 DEP FERC Form 1," "2022 DESC FERC Form 1" — hosted by South Carolina's state energy office as public mirrors of the FERC filings. Direct content fetch of these specific PDFs was blocked (HTTP 403 from both the state-hosted copies and a Duke Energy investor-relations mirror) — this looks like host-side bot-blocking rather than the data being non-public (these documents are legally required to be public), so the finding here rests on the confirmed existence/naming of the filings plus the structured field list below, not a directly-read sample.
- **Independent structural confirmation:** the open-source PUDL project (Catalyst Cooperative, `docs.catalyst.coop/pudl`) already parses FERC Form 1's raw XBRL into clean per-utility tables — "plant-level operations, utility assets & liabilities, and utility income & expenses" — and publishes the result as a free DuckDB/SQLite file at `s3://pudl.catalyst.coop`. This is strong secondary evidence the underlying government data really is per-company and really is usably structured (someone else already built the exact pipeline Scrooner would need).
- **Real correction to the hypothesis:** "allowed ROE" (what the hypothesis listed as a target metric) is **not** in FERC Form 1 at all — Form 1 shows *achieved/earned* return, while *allowed* ROE is set by individual state Public Utility Commissions in rate-case orders, scattered across 50 states' own dockets with no single federal aggregator. That part of the hypothesis needs to be dropped or re-scoped to "achieved ROE" only.
- **Format/cost:** XBRL since 2021 (needs an XBRL parser — or reuse PUDL's existing open pipeline instead of building from scratch), rate base/customer-count/revenue data all present. Real per-company data confirmed, but building it in-house (vs. leaning on PUDL) is meaningfully higher effort than the bank/airline sources above.

## Pharma / Biotech

**Hypothesis:** FDA Orange Book, ClinicalTrials.gov — confidence Medium-high.

**Verdict: usable now.** Second-strongest match in this study, and confirmed live end-to-end.

- **ClinicalTrials.gov API v2** (`https://clinicaltrials.gov/api/v2/studies`) — no API key required. Live query `?query.spons=Pfizer&pageSize=3` returned real records, including NCT01673178, a real completed Phase 1 Pfizer trial (PF-05231023, Type 2 diabetes), with fields `nctId`, `briefTitle`, `sponsor`, `phase`, `overallStatus`, `conditions`, `enrollmentCount` all populated and real.
- **openFDA Drugs@FDA API** (`https://api.fda.gov/drug/drugsfda.json`) — no API key required for basic queries. Live query confirmed real structured data: application number, sponsor name, per-submission approval dates/status, and linked approval-letter PDFs (real example pulled: ANDA077533, terbinafine, sponsor InvaGen Pharms, 7 real submission records with dates back to 2007).
- **FDA Orange Book** (patent/therapeutic-equivalence data) — confirmed as a real, official, downloadable dataset (flat text files + third-party mirrors on NBER/Kaggle exist precisely because it's public-domain government data); this session could not pin down the exact live openFDA query syntax for the Orange Book endpoint specifically in the time available, so treat that one sub-source as "confirmed to exist, not yet live-sampled" rather than fully verified like the two above.
- **Metrics investors need:** trial phase/status/enrollment (pipeline depth — arguably the single most stock-moving data point for a clinical-stage biotech), sponsor identity, drug approval/patent-expiration timing.
- **Why this ranks high:** both working sources are plain REST/JSON, free, no scraping or PDF extraction required, and map directly onto exactly the metric investors in this sector actually trade on (binary trial readouts, exclusivity cliffs).

## Mining / Metals

**Hypothesis:** USGS, industry-level only — confidence Low.

**Verdict: hypothesis's low-confidence "no per-company data" instinct was right about USGS specifically — but there IS a real per-company government source elsewhere: SEC Reg S-K Subpart 1300.**

- **USGS Mineral Commodity Summaries confirmed industry/national-level only** — live check found no per-company mine production breakdown; USGS itself states it does not directly measure company reserves.
- **Real correction:** SEC's Regulation S-K Subpart 1300 (effective FY2021+, replacing old Industry Guide 7) requires standardized, CRIRSCO-based (measured/indicated/inferred resources, proven/probable reserves) disclosure **per material property/mine**, in a mandatory tabular format, inside every mining registrant's 10-K.
- **Live sample confirmed:** Freeport-McMoRan's FY2024 10-K "Estimated Recoverable Proven and Probable Mineral Reserves" table — real, named, mine-level rows, e.g. **Morenci mine: 525 million metric tons proven reserves (0.33% Cu grade) + 50 million metric tons probable (0.32% Cu grade)**; FY2025 preliminary consolidated total cited as 112.3 billion lbs copper, 20.6M oz gold, 3.5B lbs molybdenum.
- **Verdict detail: usable with real effort.** This is real, mandatory, standardized-format, per-mine data — arguably richer than most other sectors' sources — but it lives in 10-K tables/exhibits (Technical Report Summaries), not a bulk government API; needs per-company/per-filing extraction, similar effort profile to the oil & gas case above.

## Telecom

**Hypothesis:** None identified — FCC data industry-level only — confidence Low (likely correct).

**Verdict: confirmed — no free source exists for the actual investor KPIs (ARPU, subscriber counts, churn).**

- FCC's Broadband Data Collection / National Broadband Map (`broadbandmap.fcc.gov`) does have a genuine **per-provider** download ("By Provider" tab, provider name searchable) — but it reports broadband **location-level availability/coverage**, not subscriber counts, revenue, or churn. This is a network-coverage census, not a financial-performance dataset.
- Historical FCC Form 477 did include subscriber counts by provider at the census-block level, but that program has been superseded by BDC and was never a financial KPI source (no ARPU, no revenue).
- **No standardized ARPU/churn/subscriber-count government dataset was found.** These remain entirely self-reported by telecom companies in earnings releases and 10-Ks, with no common XBRL tag and no government equivalent.
- **Verdict confirmed as hypothesized: no free official source** for the metrics that actually matter to telecom investors.

## REITs

**Hypothesis:** None identified — NAREIT-defined non-GAAP, self-reported — confidence Low (likely correct).

**Verdict: confirmed — no free government source exists.**

- FFO **does** have a standardized *definition* — but from NAREIT, an industry trade association, not a regulator, and NAREIT itself maintains no public per-company database of computed FFO values.
- AFFO has **no** standardized definition at all, confirmed live via NAREIT's own materials: "there is no standardized definition of AFFO; financial statement users should understand how the measure is defined by the company."
- Both are disclosed only inside each REIT's own 10-K MD&A as a non-GAAP reconciliation table, using company-specific XBRL extension tags rather than one common `us-gaap:FundsFromOperations` element (an attempted live check of a real REIT's XBRL company-concept endpoint for this tag was blocked by a 403 before confirming the exact tag-name situation, but the underlying "non-GAAP, extension-tag, no universal element" pattern is well-documented and consistent with what this project's own Mapper has already hit with other non-standard concepts, e.g. AAPL's 3 revenue tags per CLAUDE.md).
- **Verdict confirmed as hypothesized: no free official source.** Disclosed in filings only, and harder than most non-REIT concepts because even the *definition* of AFFO varies company to company — same taxonomy-drift problem Scrooner's Mapper already has a documented pattern for, just harder since there's no regulator-set canonical form at all.

## Insurance

**Hypothesis:** NAIC (partial, may be paywalled) — confidence Low.

**Verdict: mostly confirmed — NAIC's real per-company financial detail is paywalled; free tier is thin.**

- NAIC's InsData product (`insdata.naic.org`) sells individual insurer financial statements (PDF) as a paid product — confirmed via NAIC's own wiki that a free "Company Overview Report" exists, but its content (does it include combined ratio/loss ratio detail, or just company identity/contact info?) could not be confirmed live — the actual PDF sample fetched came back as unreadable/corrupted binary through the automated tool, so this is a genuine gap in this pass, not a confident "yes it has ratios."
- State insurance-department **SERFF** portals (e.g., Delaware's `insurance.delaware.gov/serff/`) are confirmed free/public, but they carry rate/form *filings* (policy language, rate changes) — not standardized per-company financial-ratio data.
- No standardized SEC XBRL tag for combined ratio/loss ratio was confirmed to exist — these remain non-GAAP, statutory-accounting metrics that individual insurers report in their own 10-K MD&A, not in a common `us-gaap` element.
- **Verdict: usable with real effort at best** — either paying for NAIC's InsData product (breaks "free"), or per-company 10-K MD&A text extraction (unstructured, no standard tag). Largely confirms the Low-confidence hypothesis.

## Retail

**Hypothesis:** None identified — confidence Very low (likely "no free source").

**Verdict: confirmed — no free source exists, and no government angle at all (retail isn't a regulated industry).**

- No standardized `us-gaap` XBRL tag for "same-store sales" or "comparable sales" was found — live search confirms this remains a voluntary, inconsistently-defined disclosure companies make in earnings press releases (often an 8-K exhibit) and 10-K MD&A prose, never a government dataset.
- **Verdict confirmed: no free source exists.** This is the hardest sector in the whole study to ever get structured data for — even the underlying SEC filing itself doesn't reliably carry it in extractable form for every retailer, since it's frequently only in the earnings press release, not the 10-K body.

## Homebuilders

**Hypothesis:** Census Bureau (industry-level only) — confidence Very low (likely correct).

**Verdict: confirmed — Census data is industry/regional aggregate only.**

- Census Bureau's Survey of Construction / New Residential Construction release is confirmed, live, to report only "national level and by census region" figures — explicitly not broken out by builder company.
- Backlog, closings, and cancellation rate remain self-reported by each homebuilder in its own 10-Q/10-K, with no confirmed standard XBRL tag for backlog/cancellation-rate specifically (some generic real-estate unit-count tags may exist but not these specific metrics).
- **Verdict confirmed: no free government source.** Company-filing-only, unstructured.

## Semiconductors

**Hypothesis:** SIA (industry aggregate only) — confidence Very low (likely correct).

**Verdict: confirmed, and slightly worse than hypothesized.**

- SIA's Databook is a **paid** product (pricing requires contacting SIA directly) — not free even at the industry-aggregate level.
- SEMI's monthly Book-to-Bill report — the other historical source people cite for this metric — was **discontinued in 2017** (last published December 2016), confirmed live.
- Book-to-bill is inherently a company/supply-chain-specific metric (a firm's own orders-received vs. shipped), not something any government agency collects.
- **Verdict confirmed: no free source exists,** and even the aggregate industry-level version is now weaker than the original hypothesis assumed.

---

## New sectors added beyond the brief's starting list

### Auto manufacturers (new — genuinely good find)

- **Source:** EPA Automotive Trends Data (`epa.gov/automotive-trends/explore-automotive-trends-data`) + NHTSA's CAFE Public Information Center (`nhtsa.gov/corporate-average-fuel-economy/cafe-public-information-center`).
- **Confirmed live:** the EPA tool explicitly supports filtering/downloading by **Manufacturer** (Ford, GM, Tesla, Toyota, Stellantis, etc.), with CSV export, covering model years 1975-2025 — fuel economy, CO2 emissions, and vehicle-attribute trends per manufacturer. NHTSA's CAFE PIC (direct fetch blocked, HTTP 403, but its own program description confirms per-manufacturer CAFE compliance/credit-deficit data, downloadable as Excel/PDF).
- **Investor relevance:** CAFE credit deficits are a real forward-looking cost/regulatory-risk signal (an automaker running a compliance deficit either buys credits from a competitor like Tesla or faces fines) — a genuinely differentiated, not-generic metric.
- **Verdict: usable now** for the EPA half (fuel economy/CO2 by manufacturer, live-confirmed downloadable); moderately lower priority than the top sectors below because the US-listed automaker universe is small (~4-5 tickers: F, GM, TSLA, plus a couple of truck makers), limiting how much screening value it adds relative to build effort.

### Trucking / shipping / logistics (new — checked, low value)

- **Source checked:** FMCSA's SAFER Company Snapshot (`safer.fmcsa.dot.gov`) — confirmed free, live, no-login, per-carrier lookup by USDOT/MC number or name.
- **Finding:** this is safety/compliance/registration data (crash history, out-of-service rates, active authority) — **not** the financial/operational KPIs investors actually screen trucking/logistics stocks on (revenue per loaded mile, tonnage, operating ratio). No free government source for those exists.
- **Verdict: no free source for investor-relevant KPIs.** Not worth pursuing; noted here mainly to close off the question rather than recommend building it.

---

## Also checked, not sector-specific (per the brief's explicit ask)

**SEC DERA Financial Statement Data Sets** — confirmed real and free (`sec.gov/dera/data/financial-statement-and-notes-data-set`). Two tiers exist: the older "Financial Statement Data Sets" (SUB/TAG/NUM/PRE files — face-financials only, standard + custom tags) and the fuller "Financial Statement and Notes Data Sets" (adds footnote-level text and numeric detail). The face-financials tier is almost certainly redundant with what Scrooner's Collector already gets per-company via the `companyfacts`/Frames APIs (same underlying XBRL facts, just bulk-packaged instead of per-CIK). The **Notes** tier is the one part not already covered — it captures footnote *text* disclosures (which could include some of the oil-and-gas/FFO/insurance narrative content discussed above) in bulk, quarterly ZIP form — worth a future narrow look if any sector's non-numeric footnote text becomes a real target, but not needed for anything currently in scope.

**FRED / U.S. Treasury** — confirmed real, free, well-documented REST API at `api.stlouisfed.org/fred/`, free API key, 120 calls/minute, 800,000+ series including `DGS10` (10-year Treasury), `FEDFUNDS`, `MORTGAGE30US`. Not per-company, but exactly the kind of free macro input the brief flagged as useful for a future valuation-context feature (e.g., a risk-free-rate input to a cost-of-equity/WACC-based flag). Trivial to add whenever that feature is prioritized — no blocker found.

---

## Ranked recommendation: best 2-3 sectors for Scrooner to pursue next

Ranking on **effort vs. investor value**, using only what was actually confirmed live above:

### 1. Pharma / Biotech — build first
Two free, no-auth, plain-JSON REST APIs (ClinicalTrials.gov v2, openFDA Drugs@FDA) both confirmed working end-to-end this session with real data for a real company. Zero scraping, zero PDF extraction, zero XBRL-tag archaeology — the lowest engineering lift of any sector in this study. The metric (trial phase/status, pipeline depth) is also uniquely high-leverage for this sector specifically: clinical-stage biotech valuations are driven almost entirely by pipeline/trial-readout risk, more so than any standard financial ratio Scrooner already computes. Sponsor-name matching (ClinicalTrials.gov sponsor field is free text, not a CIK/ticker) is the one real integration task, and it's a fuzzy-match problem Scrooner's Mapper already has practice with (taxonomy-drift handling).

### 2. Banks — build second
Also a clean free REST JSON API (FDIC BankFind Suite), live-verified with real NIM/efficiency-ratio numbers for JPMorgan Chase Bank, decades of quarterly history, no auth required. The one real engineering task is mapping FDIC bank-charter CERT numbers to public holding-company tickers/CIKs — solvable using FFIEC's free NIC hierarchy data, not a blocker. High investor value: NIM, efficiency ratio, and NPL ratio are exactly the metrics serious bank investors screen on, and the US has hundreds of publicly-traded regional/community banks this would newly unlock, not just the money-center names.

### 3. Airlines — build third
DOT's Form 41 data (T-100 traffic + P-1.2/P-6 financials) is real, free, CSV/SQL-downloadable, and enables RASM/CASM/load-factor calculation for a well-defined universe of ~12-15 major US carriers. Slightly more build effort than banks/pharma (needs joining two separate schedules rather than one clean endpoint, and carrier-code-to-ticker mapping), but still no PDF/HTML scraping required — everything is in structured CSV/tabular government data.

**Explicitly not recommended next**, despite real free data existing: **Regulated utilities** (FERC Form 1 is real and per-company, but is the highest-effort "real" source found — XBRL parsing or dependence on a third-party pipeline like PUDL, plus the most commonly-wanted metric, allowed ROE, isn't even in it) and **Mining/Metals** (SEC S-K 1300 reserve tables are real and richly detailed, but require per-filing table extraction with no bulk API, and the mining-issuer universe on US exchanges is smaller than banks/airlines/pharma). Both are legitimate follow-ons once the top 3 are built, not this round's best move.
