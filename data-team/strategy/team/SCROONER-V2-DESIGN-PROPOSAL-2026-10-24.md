# Scrooner V2 data design: proposal (Head of Data Product, 2026-10-24)

PROPOSAL only: the founder decides; accounting definitions need a named reviewer. Inputs: the atlas (same folder), the as-filed pilot and the founder statement (PLAN.md), and doc 34.

## Decision sheet: the three calls only the founder can make
| # | Decision | Options | Recommendation |
|---|---|---|---|
| 1 | Make the hybrid (API values + company slot records + format gate) the primary route for the top-1000, with visible holds ("format changed, under review") | (a) yes, cohort first; (b) keep the global tag lists; (c) filing-only | **(a)**. Pilot: hybrid fixed 13 of 16 known-wrong cells (filing-only 10); the filing read broke no correct value except 185 par-value truncations (FSDS 4-decimal limit) |
| 2 | May furnished, unaudited 8-K Ex-99.1 numbers be shown: Q4 discrete per-share and revenue, and company guidance? | (a) Q4 only, labelled "earnings release, unaudited", tied to FY minus 9M; (b) Q4 and guidance; (c) neither | **(a)**. Guidance waits: doc 02 keeps analyst forecasts out, and guidance is close to that line |
| 3 | Data budget: load FSN for the cohort (about 0.3 GB per peak month, streamed, cohort rows kept) and stop growing `core.fact` with unmapped note facts | (a) yes, plus a measured size pilot; (b) keep companyfacts only | **(a)**, gated on a one-month size pilot |

**Evidence.** The API is exact where it reaches (93.4% of face facts; 0 standard face facts missing) and carries the note facts (48% of stored us-gaap facts). It lacks dimensions (682 of 1,421 facts in MU's FY2026 10-K), custom tags (6.4%), text, dei flags and presentation. Wrong values are structural (perimeter, total line, vintage, split basis), not extraction errors.

## Architecture
**1. Sources**
| Need | Source | Cadence |
|---|---|---|
| Values, standard tags | companyfacts API per new filer (as today) | Nightly |
| Structure, dimensions, notes, text, calc trees | FSN bulk (superset of FSDS) | Monthly, 1-5 weeks lag |
| Gate fingerprint before FSN | FilingSummary.xml, MetaLinks.json, `_cal.xml` (3 requests, 1.5 MB) | Per filing, XBRL RSS trigger |
| Custom-tag values on held slots | Instance (`_htm.xml`) | Only on a gate hold |
| Events | Submissions `items` and form types (add NT 10-K/Q, 25) | Already fetched |
| Q4 per-share | 8-K 2.02 Ex-99.1, cohort only | About 4 a year per company |
| Ownership | Insider data sets (bulk, quarterly), SCHEDULE 13D/G XML, 13F/N-PORT bulk | Quarterly / per filing |

**2. Storage.** Keep `raw`, `core.fact` and `is_authoritative`. Add three small cohort tables from FSN: `filing_line` (PRE), `filing_calc_arc` (CAL), `fact_dim` (slot axes only: segments, geography). Never store full instances or text blocks; store flags plus accession and R-file.

**3. Mapper table.** `analytics.company_slot_record`: company, statement, slot (e.g. `total_debt.current_borrowings`), member tags and weights, calc parent, effective period range, evidence accession, fingerprint hash, status (proposed / verified / retired), verifier. Built from 2015+ FSN. Global `concept_mapping` remains the fallback outside the cohort.

**4. Format-change gate (every new 10-K/10-Q).** Fingerprint = ordered (statement role, line tag, calc parent, weight) for face statements and slot-relevant note roles. Same: map from the API. Different: hold only the affected slots with the visible reason, fetch the instance, Tag Mapper proposes, Verifier (accountant if a definition changes) checks, then release. Known break classes: ASC 842, ASC 606, CECL, bank InterestExpenseOperating (2021-09), ASU 2023-07 segments, ASU 2023-09 tax, FYE change (8-K 5.03), new CIK (8-K12B).

**5. Derivation with proof stamps.** One stamp per value: `filed` (fact id), `filed_sum` (named calc arcs, one accession), `period_arithmetic` (FY minus 9M, same vintage, additive allowlist), `earnings_release` (Ex-99.1, tied to period arithmetic), `split_rebased` (split event id), `held` (reason). No stamp, no display; no per-share subtraction.

**6. Serving.** The screener snapshot reads only stamped values at certificate state `checks_clean` or better; "why this number" shows stamp, accession, R-file.

**7. Certificate.** Keep I1-I11; add I12 (slot record verified for the period) and I13 (event flags shown: 4.02, NT filing, auditor change, going concern). R1 reconciles against FSN NUM. Badges: "restatement disclosed", "auditor changed", "late filer".

## Same / changes / stop
- **Same:** companyfacts as value feed; Collector boundaries; `is_authoritative`; certification suite; Verifier sampling.
- **Changes:** structure from each filer's own presentation and calc tree, per era; FSN replaces FSDS; narrow visible holds; proof stamps.
- **Stop:** growing global tag-precedence lists as the main mapper for the cohort; label heuristics for total lines; per-filing Form 4 fetches (about 38,000 a quarter, replaced by one 8.7 MB zip); validating "latest filed" rules with Frames; relying on Financial_Report.xlsx.

## Build order (coverage up, data consumption down)
| Step | Work | Metric (baseline -> target) | Owner |
|---|---|---|---|
| 0 | Fix the SCHEDULE 13D/G form types + XML parse (classPercent, shares) | 13D/G rows per quarter 2-19 -> 1,000+ | Data Engineer |
| 1 | FSN one-month size pilot, cohort rows only | Rows/GB measured; decision 3 | Data Engineer |
| 2 | Slot records for debt, D&A, capex, revenue total and operating income on the 30-company set; replay the 16 known-wrong cells | Fixed 13 -> 16 of 16; 0 regressions | Tag Mapper + Verifier |
| 3 | Gate on new cohort filings (RSS trigger, 3 files) | Share of new filings auto-mapped; hold time < 5 days | Data Engineer |
| 4 | Proof stamps + Ex-99.1 Q4 (per decision 2) | Unclassified Q4 cells (top-1000 q4_not_derived 5,801, doc 34) -> 0 unclassified | Period Engineer |
| 5 | Event flags (zero fetch): 4.02, 4.01, NT, 25, 3.01 | Flags live for 1,000 companies | Data Engineer |
| 6 | Insider bulk sets replace the Form 4 fetch; Forms 3/5 added | Requests per quarter about 38,000 -> about 1 | Data Engineer |
| 7 | Map the note schedules already in `core.fact` (debt ladder, leases, cash taxes, RPO, buyback authority, pay vs TSR) | New screenable fields: 0 -> 6, each with a coexistence check | Tag Mapper + Standardization Lead |
| 8 | Segments and geography from FSN DIM with sum-to-total checks | Cohort companies with verified segments: 0 -> 1,000 | Sector Analyst |

**Risks.** A wrong slot record is wrong for a whole era (hence evidence accession + Verifier status); holds can pile up in 10-K season. **What would change my mind:** step 2 breaks any stored-correct cell, or step 1 shows cohort FSN rows above about 2 GB.

## Could not verify
FSN zip contents; how often fingerprints change (ASSUMED low, per the founder); Ex-99.1 parse reliability across filers; effort (not estimated).
