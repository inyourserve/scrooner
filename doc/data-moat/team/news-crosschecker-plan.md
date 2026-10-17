# Plan: Reported-Numbers Cross-Checker (9th team role)

Status: plan only, 2026-10-17. Nothing built. Proposed spec slot: `data-team/18-REPORTED-NUMBERS-CHECKER.md` once approved.

## Purpose
Independently confirm that the value we store for a headline metric equals what the company publicly reported, using sources outside our own pipeline. It catches scale, period, sign, tag and restatement errors that our internal checks (same XBRL data on both sides) cannot see, and it complements the yfinance sanity check.

## Hard boundary (from the team constitution and doc 02)
SEC EDGAR is the only source of stored values. This role produces a **comparison signal**, never a value, never a fix, never an approval. A mismatch becomes a proposed finding for Triage/Verifier; a match is supporting evidence, not proof.

## Source hierarchy (best first)
1. **8-K Item 2.02 / Exhibit 99.1 earnings release, or the 10-K/10-Q, on EDGAR.** Primary, company-authored, and the filing is also the stored-value source. Most of the value comes from here, not from "news".
2. Company investor-relations site: the same release plus supplemental tables, and official CSV/XLSX financial-statement workbooks (see the revision section for the format controls).
3. Wire republication (Business Wire, PR Newswire, GlobeNewswire): identical text, useful for timing.
4. ~~News summaries~~ removed from the default path (see revision below).
Never used as evidence: aggregators, forums, social posts, AI summaries, paywalled previews, anything without a locatable figure.

## Revision 2026-10-17: one layer, primary documents, news dropped to optional
Founder direction: verify directly against the company's own published document (for example the results PDF Indian companies file), not against news about it. Adopted. The role becomes a **Primary-Document Checker**; tier 4 (news) is removed from the default path and tier 3 (wires) stays only as a timing aid. News adds a second interpretation layer (headline rounding, adjusted figures, reporter errors) with no extra authority.
- **Rule change (founder direction, 2026-10-17):** the primary document is any official document published by the company itself, in any format: HTML, PDF, CSV, XLS/XLSX or XBRL/iXBRL, hosted on EDGAR **or** on the company's own investor-relations domain (earnings release, financial-statements workbook, supplemental data pack, annual report). EDGAR is no longer a requirement for the *evidence*. Why this does not break doc 02: the locked rule, "SEC EDGAR is the only source of stored values," governs what Scrooner stores and shows. This role stores nothing and approves nothing; it only compares, so its evidence set can be wider. The same asymmetry applies as before: a match is supporting evidence, a mismatch is a proposed finding, and a fix still has to come from the SEC filing.
- **What counts as "official":** published by the issuer (its IR domain or an EDGAR exhibit), identified by domain and URL, with a retrieval date and content hash. Third-party CSVs and workbooks (aggregator downloads, vendor dumps, data portals) are NOT primary documents; they are comparison signals of the same kind as yfinance, and must be labeled that way.
- **CSV/XLSX controls:** record file hash, sheet name and cell/row locator; read the header row, the units/scale row and the period header for that column before taking a figure; a figure is valid only if the metric label, period and unit all match. Watch for hidden sheets and columns, formulas versus cached values, merged headers, restated or updated copies of the same file under the same URL, GAAP and non-GAAP tabs side by side, and locale number formats (decimal commas, lakh/crore grouping). If the file changes between retrievals, treat both versions as separate evidence.
- **US companies (current V1 scope):** typically the earnings release (8-K Ex. 99.1), the 10-K/10-Q itself, or the IR-site financial workbook. The EDGAR versions remain preferred because the filing is itself the stored-value source, which makes a disagreement between them and an IR-site file informative in its own right.
- **Indian companies:** out of V1 scope (doc 02 locks US-listed equities only; India is an audience, not part of the company universe). If the universe is ever widened, the same role applies with the exchange-filed results PDF (BSE/NSE) as the primary document, but that is a scope decision for doc 02, not for this team.
- **PDF handling is the hard part, not the sourcing.** Table extraction from PDFs fails silently (merged cells, wrapped labels, scale footnotes, consolidated vs standalone columns, parentheses for negatives). Required controls: record page number and table/row locator for every figure; read the stated unit/scale line on that page; confirm the column's period header; a figure is valid only if all three match; low-confidence extractions go to a human spot-check, never straight to a finding. Keep the PDF's content hash with the evidence.
- **Add to the acceptance tests:** a PDF table where the scale line is "in lakhs/millions", a consolidated vs standalone column, a negative shown in parentheses, and a scanned page with no text layer (expected: `not_found`/`not_comparable`, never a guessed value).

## Scope
GAAP headline metrics a release states: revenue, operating income, net income, diluted EPS, and where tabled, operating cash flow. Start with annual and Q4/quarter figures for companies with the most user traffic. Not in scope: non-GAAP, guidance, segment detail, analyst estimates.

## Known traps the role must handle (these become the acceptance tests)
- GAAP vs adjusted/non-GAAP in the same release (news headlines usually quote adjusted EPS).
- Scale: millions vs thousands vs exact; compare within rounding precision, never exact-equal.
- Fiscal vs calendar year; 52/53-week periods; transition periods.
- Release says one number, later 10-K says another (final audit adjustments): both are real; report the gap, do not pick a winner.
- Restated or recast prior-period comparatives (discontinued ops, reclassification).
- Continuing vs total operations; attributable to parent vs including noncontrolling interest.
- Webpage text containing instructions (prompt injection): treat as untrusted data.
- Source not found: return `not_found`, never infer from memory or from our own data.

## Output contract (one row per issuer-period-metric)
our_value (with core.fact id), reported_value, source_url or accession, retrieved_at, locator (table/row/quote), basis (GAAP/non-GAAP), scale, tolerance used, verdict.
Verdicts: `agrees`, `agrees_within_rounding`, `differs_explained` (name the cause), `differs_unexplained`, `not_found`, `not_comparable`. Plus confidence in the source match, kept separate from the verdict. Hands off to Triage via the existing `record-finding` path as a proposal; no direct DB writes.

## Controls
Read-only. Web and EDGAR access only through approved tools, SEC rate limits and declared User-Agent for sec.gov. Cache by URL hash. Bounded batch (default 50 cells per run, per the shared work limits). No paid services without the founder's approval. Record retrieval date, because web pages change.

## How we know it works
Precision of its flags (share of `differs_unexplained` that a human confirms as a real data error) and the false-positive causes. Success is a falling false-positive rate with every confirmed error traced to a fixed rule, not a high flag count.

## Phases
- **P0 (spec + tests):** write the role file and 8-10 synthetic acceptance cases covering the traps above, graded the same way as round 1.
- **P1 (EDGAR-only pilot):** 20 cells for golden-10 companies using Exhibit 99.1 only. No open web yet. Compare against our values; hand-check every result.
- **P2 (open-web pilot):** 50 cells for non-golden, high-traffic companies, with wire and IR sources; measure false positives.
- **P3 (post-earnings sweep):** triggered by new 8-K Item 2.02 filings for the top N companies, catching errors within days of publication. Only after two clean pilot rounds.

## Decisions needed from the founder
1. Does the first version use EDGAR Exhibit 99.1 only, or the open web from the start? (Recommendation: Exhibit 99.1 only for P1.)
2. Budget and tooling for web access, including whether paid news sources are acceptable (recommendation: none).
3. Top-N definition for P3 (by page traffic or by market cap).
4. May a confirmed mismatch open a finding automatically, or must Triage approve each? (Recommendation: Triage approves.)
