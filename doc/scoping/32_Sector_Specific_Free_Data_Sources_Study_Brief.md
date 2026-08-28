# Doc 32 — Research Brief: Sector-Specific Free/Official Data Sources for US Equities

**Status:** Draft brief (2026-08-27) — a work order for a dedicated research pass, not yet executed. Owner: Founder/Product.

---

## Context

Scrooner is a US-equity fundamental-screening product. Its data pipeline (`pipeline/` in this repo) already ingests SEC EDGAR data (10-K/10-Q financials, ownership filings) for the full US-listed operating-company universe, and computes ~20+ standard financial ratios (margins, ROE/ROIC, growth, leverage, quality flags) that apply to *any* company regardless of industry.

The gap this brief is about: **many industries have their own sector-specific KPIs that serious investors actually care about, which the standard financial-ratio set doesn't capture** — the way a bank investor cares about Net Interest Margin, or a telecom investor cares about ARPU and subscriber counts. Some of these metrics have a clean, free, **official government/regulatory source** (a real data moat opportunity — same reasoning that made SEC EDGAR itself Scrooner's core data moat: free, redistributable, no vendor lock-in). Others exist only inside each company's own filing text, with no government equivalent.

## The task

Do a **complete, live-verified study** — not a desk-research guess — of which major US equity sectors have a real free/official data source for their sector-specific investor metrics, and which don't. For each sector below (and any other major sector worth adding), determine:

1. **What are the 3-5 metrics a serious investor in this sector actually needs**, beyond generic margins/ROE/growth?
2. **Is there a free, official (government/regulatory) source for company-level data on these metrics** — not an industry-aggregate stat, a real per-company figure?
3. **If yes:** what's the actual URL/API/bulk-download mechanism, what format is the data in, how far back does history go, and — critically — **fetch and inspect one real record for one real company** to confirm the claim before writing it down as fact. (This project's own discipline, documented throughout its `doc/` folder: never assert a data source works from memory or a plausible-sounding claim — check a live sample first.)
4. **If no clean government source exists:** confirm whether the metric is at least disclosed in the company's own SEC filings (10-K/10-Q MD&A section, or a dedicated XBRL tag/extension) — even if unstructured, that's a different (harder, but not impossible) path than "no source exists at all."
5. **Rough fetch/build cost**: is this a one-time bulk download, a per-company API call, or something requiring HTML/PDF text extraction?

## Starting hypothesis list (verify, don't assume)

This is a first-pass guess from general domain knowledge — every row needs live verification, several may turn out wrong or outdated:

| Sector | Candidate metrics | Candidate free source | Confidence |
|---|---|---|---|
| Banks/Financial Institutions | Net Interest Margin, efficiency ratio, Tier 1 capital ratio, NPL ratio, loan-to-deposit ratio | FDIC BankFind / Call Reports, FFIEC Central Data Repository | Medium — needs live check of per-company match rate |
| Airlines | RASM/CASM, load factor, available seat miles | DOT Bureau of Transportation Statistics (Form 41 / T-100 data) | Medium |
| Oil & Gas / Energy (E&P) | Proved reserves, production volumes (bbl/day), reserve replacement ratio | EIA (Energy Information Administration) | Medium |
| Regulated utilities | Rate base, allowed ROE, customer counts | FERC Form 1 (electric utilities) | Medium |
| Pharma/Biotech | Clinical trial phase/status, drug patent expiration | FDA Orange Book, ClinicalTrials.gov | Medium-high |
| Mining/Metals | Proved/probable reserves, production volumes | USGS (industry-level only, likely not per-company) | Low |
| Telecom | ARPU, subscriber counts, churn | None identified — FCC data is industry-level only | Low (likely "no clean source" — confirm) |
| REITs | FFO, AFFO, occupancy rate, same-store NOI | None identified — NAREIT-defined non-GAAP, self-reported | Low (likely "no clean source" — confirm) |
| Insurance | Combined ratio, loss ratio, underwriting expense ratio | NAIC (partial, may be paywalled) | Low — needs a real check of what's actually free vs. member-only |
| Retail | Same-store sales, sales per square foot | None identified | Very low |
| Homebuilders | Backlog, closings, cancellation rate | Census Bureau (industry-level only) | Very low |
| Semiconductors | Book-to-bill ratio | SIA (industry aggregate only) | Very low |

Also worth checking while at it, not sector-specific:
- **SEC DERA Financial Statement Data Sets** — a separate bulk dataset from `companyfacts`; check whether it's redundant with what Scrooner already extracts, or offers something new.
- **FRED / U.S. Treasury** — free interest-rate/macro series (not per-company, but a real input for any future valuation-context feature).

## What "complete" means here

For each sector in the table (plus any other major sector you judge worth adding — e.g. auto manufacturers, agriculture/farming, shipping/logistics):

- State the real, current metrics investors in that sector actually use (don't just repeat the hypothesis list uncritically — correct it if your own research disagrees)
- Name the actual source (exact agency/dataset name), with the real URL/API endpoint
- Report a live-fetched sample: one real record for one real, named company, showing the actual fields available
- Give an honest verdict: **usable now**, **usable with real effort** (specify what kind), or **no free source exists**
- Flag anything that turned out different from the starting hypothesis above — being wrong and correcting it is expected and useful, not a failure

## Output format

A single markdown report, one section per sector, in the same evidence-first style as this project's own `doc/scoping/` and `doc/execution-plans/` documents — real findings with real URLs/samples, not general claims. End with a ranked recommendation: which 2-3 sectors are the best next move for Scrooner, given effort vs. investor value.
