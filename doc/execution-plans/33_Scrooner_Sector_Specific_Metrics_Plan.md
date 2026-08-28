# Doc 33 — Sector-Specific Metrics: Build Plan

**Status:** Draft (2026-08-27) · Owner: Founder/Product · Review: after doc 32's research pass returns real findings

**Gated on doc 32.** This is the *build* plan for what doc 32's research brief asks someone to verify. Nothing here should actually be built until doc 32's live-verification step confirms each source really works the way the hypothesis assumes — this doc lays out what we'd do *if* it checks out, in what order, and names the one real risk common to all of it.

---

## The one risk that applies to every sector: the company crosswalk

Every sector-specific government source (FDIC, DOT, EIA, FERC, FDA) identifies companies by **its own ID**, not by SEC CIK — an FDIC certificate number, a DOT carrier code, an EIA operator ID, a FERC docket number, an FDA sponsor name. None of these map to our `core.company.cik` for free out of the box.

**This is not a new problem — Scrooner already solved this exact shape once.** Doc 19's Form 13F institutional-ownership build hit the identical issue (13F identifies holdings by CUSIP, not CIK) and solved it by extending an existing parser to also capture the missing identifier from a filing's own cover page, rather than paying for an external crosswalk vendor (`doc/learnings/form-13f-cusip-crosswalk.md`). The same playbook applies here: check whether the target company's own SEC filings (10-K cover page, exhibits, or MD&A) already disclose the regulator-specific ID we'd need (banks routinely disclose their FDIC certificate number or RSSD ID in filings; airlines' DOT certificate numbers are public; EIA operator IDs are sometimes in 10-K reserve disclosures). If they don't, the sector isn't buildable without a paid crosswalk, full stop — this check has to happen *before* any schema or fetch code, not after.

## Code architecture: separate modules per source, one service

**Separate code modules — yes, following an existing precedent.** Every external data source Scrooner already integrates gets its own client module inside the single `pipeline/` package: `common/sec_client.py`, `common/alpaca_client.py`, `ownership/institutional.py` (Form 13F's own crosswalk logic). The same pattern extends directly:

```
pipeline/src/scrooner_pipeline/sector_data/
├── fdic_client.py       # banks -- Net Interest Margin, efficiency ratio, Tier 1 ratio, NPL ratio
├── dot_client.py        # airlines -- RASM/CASM, load factor
├── eia_client.py        # energy -- proved reserves, production volumes
├── ferc_client.py       # utilities -- rate base, allowed ROE
├── fda_client.py        # pharma/biotech -- different shape (drug/trial-level, own sub-project)
└── crosswalk.py         # shared: company_id <-> external-source-ID mapping, one table, reused logic
```

One shared CLI entry point, `jobs/sector_data.py`, with a Typer subcommand per sector (`update-bank-metrics`, `update-airline-metrics`, `update-energy-metrics`, ...) — mirroring how `jobs/ownership.py` already holds three different form-types' commands (Form 4, 13D/13G, 13F) in one file rather than three separate files.

**Separate deployed services — no.** Each of these is periodic batch ingestion (fetch a bulk file or hit an API, parse, write to Postgres) — the same shape as everything already in `pipeline/`. A separate service per source would mean separate deploys/monitoring/failure points with zero actual benefit: none of these need independent scaling or a different runtime, and there's no demonstrated need driving that complexity. Directly conflicts with doc 02's "No FastAPI initially" and doc 05's "prefer managed, conventional components a solo founder can operate reliably." Module-per-source inside one service, not service-per-source.

## Proposed schema pattern

Reuse the same additive discipline as `mapper/expanded_concepts.py` (doc 18/26) — new tables, never touching frozen ones:

- One new table per sector under `core` (e.g. `core.bank_regulatory_metric`, `core.airline_operating_metric`), each keyed by `company_id` + period + metric name/value — not a single generic table, since each sector's fields are genuinely different shapes (a bank's NIM/Tier-1-ratio vs. an airline's RASM/load-factor share nothing structurally).
- A `core.company_sector_identifier` table mapping `company_id` → external ID + source (e.g. `('FDIC', '628')`), the crosswalk layer itself — one small, reusable table rather than duplicating ID-mapping logic per sector.
- New sector-specific `analytics.metric_definition` rows, following the same pattern as the existing 18 locked + expanded metrics, but explicitly flagged as sector-scoped (only computed/shown for companies whose SIC code matches) — never forced onto a company the metric doesn't apply to.

## Staged build order, by confidence + effort (from doc 32's hypothesis)

### Stage 1 — Banks (FDIC/FFIEC)
**Why first:** already a named, real gap — Piotroski F-Score, Quick Ratio, and other locked metrics are *already* silently null for JPM/ARCC today because banks don't report a classified balance sheet the standard formulas expect (see `pipeline/CLAUDE.md`'s quality_score.py entry). This isn't a hypothetical nice-to-have, it's fixing an existing, visible gap.
1. Live-verify: does FDIC's BankFind/Call Report data actually cover our specific bank holding companies (not just FDIC-insured banks directly — many are subsidiaries of a public holding company, which is what actually trades)?
2. Solve the crosswalk: check whether 10-K filings for bank holding companies disclose subsidiary FDIC certificate numbers/RSSD IDs.
3. If both hold: build `core.bank_regulatory_metric` (NIM, efficiency ratio, Tier 1 ratio, NPL ratio, loan-to-deposit ratio), sourced from FDIC's own quarterly bulk data (not per-company API calls — same "prefer bulk over per-company fetch" discipline as `companyfacts.zip`).

### Stage 2 — Energy / Oil & Gas (EIA)
**Why second:** EIA has a strong reputation for clean, well-documented bulk data; oil & gas is a large, well-covered US sector.
1. Live-verify EIA's company-level (not just industry-level) production/reserves data actually exists and matches our E&P companies.
2. Solve the crosswalk (EIA operator IDs vs. CIK) — likely via 10-K reserve-disclosure text (SEC's S-K 1300 rules require this disclosure).
3. Build `core.energy_reserves_metric` (proved reserves, production volumes, reserve replacement ratio).

### Stage 3 — Airlines (DOT/BTS)
**Why third:** small company universe (a handful of major US carriers), so even if the crosswalk needs manual curation for each one, the total effort is bounded.
1. Live-verify DOT Form 41/T-100 data covers our specific airline tickers.
2. Crosswalk: DOT carrier codes are public and few enough to hand-map if no automatic source exists (same acceptable-manual-curation pattern as Company Master 4a's ticker-change confirmations).
3. Build `core.airline_operating_metric` (RASM, CASM, load factor).

### Stage 4 — Utilities (FERC Form 1)
Same shape as Stage 1-3; lower priority only because it's a smaller, more niche investor audience than banks/energy/airlines.

### Stage 5 — Pharma/Biotech (FDA/ClinicalTrials.gov)
**Different pattern, not just "another sector table":** this isn't company financials, it's drug/trial-level data that needs its own company→drug mapping (one company can sponsor many drugs, and a drug's sponsor can change hands). Scope this as its own sub-project once Stages 1-4 prove the general pattern works, not as a drop-in fifth sector.

## What NOT to build

- **Telecom, REITs, retail, homebuilders, semiconductors** — doc 32's hypothesis says no free government source exists for these; if that holds, the only path is MD&A text extraction, which is a fundamentally different (and much harder) project than anything in this plan. Don't fold it into "sector metrics" scope — it would need its own dedicated text-parsing plan, evaluated on its own merits.
- **Insurance (NAIC)** — flagged as low-confidence/possibly-paywalled in doc 32; verify before including in any stage above.

## Definition of done, per stage

Same discipline as every other Scrooner build (docs 08b/09b/11b/13b/14b/15b/16b/19): not "we wrote the code," but real evidence — a live-fetched sample record for a real company, a working crosswalk verified against the *full* target set (not one sample company — same lesson doc 19 already learned twice), and the new metric computed and hand-checked against that company's actual known real-world numbers before trusting it.
