# Scrooner Data Moat Operating Standard

Owner: Head of Data Product. Approver: founder. Applies to every data source, metric, company and release.

This document defines **how Scrooner builds a durable data business**. `data-team/strategy/THE-PLAN.md` decides current scope and sequence; the task board records execution. If they conflict, `THE-PLAN.md` wins.

## 1. The moat thesis

Public filings are not the moat. The moat is the accumulated system that turns them into trustworthy, comparable and explainable decisions:

1. Point-in-time raw evidence preserved from authoritative sources.
2. Versioned accounting definitions and industry templates.
3. Company-specific, era-specific mappings backed by filing evidence.
4. Automated invariants and independently verified exceptions.
5. Provenance from every displayed value to its source or derivation.
6. A growing history of corrections, restatements and resolved edge cases.
7. Fast, repeatable processing when new filings arrive.
8. User-visible trust: certification, reasons, change history and quality measures.

Every project must strengthen at least one of these layers without weakening another.

## 2. Non-negotiable principles

1. **Correctness before breadth.** Withhold an ambiguous value with a reason; never fill it by guess.
2. **Primary evidence first.** SEC filing evidence outranks vendor data, labels, taxonomy descriptions and model output.
3. **Reported and standardized are separate.** Preserve what the filer said; derive the comparable product value through an explicit rule.
4. **Meaning is versioned.** Mappings and definitions have company, form, period, taxonomy and effective-era boundaries.
5. **No silent overwrite.** Preliminary, filed, amended and restated versions remain distinguishable and queryable point in time.
6. **Every value explains itself.** A displayed value identifies its accession, reported facts, mapping/rule version, derivation inputs and certification state.
7. **Machines propose; evidence decides.** AI, labels and statistical similarity may generate candidates but cannot approve accounting meaning.
8. **Preparation and verification are independent.** The author of a value-changing rule cannot be its final verifier.
9. **Exceptions become assets.** A resolved case becomes a reusable, tested rule or a scoped company-era record—not an undocumented manual patch.
10. **Quality is measured publicly.** Report observed error rates and coverage states; never claim universal correctness.

## 3. The required data lifecycle

No value may bypass a stage.

### A. Acquire

- Prefer authoritative sources: SEC submissions, filings, Companyfacts and FSN.
- Record source URL, accession, retrieval time, content hash and parser version.
- Fetch incrementally; preserve the latest distinct raw payload and avoid byte-identical duplicates.
- Use releases or secondary sources for speed only when visibly labelled and later reconciled to the filing.

### B. Preserve as reported

- Store fact identity, concept, unit, scale, period, dimensions, filing and amendment lineage.
- Retain original and restated observations instead of destructively replacing history.
- Keep reported presentation separate from standardized concepts.

### C. Interpret structure

- Use statement role, presentation, calculation relationships, dimensions, labels and note context together.
- Treat FSN calculation trees as filer evidence, not automatic accounting approval.
- Detect filing-format fingerprints. A changed structure holds affected mappings for review.

### D. Standardize

- Define each canonical metric with included slots, excluded slots, applicable industries and permitted derivations.
- Maintain different templates where economic meaning differs: commercial, banking, insurance, REIT and other necessary profiles.
- Store company-slot records with effective periods and evidence accessions.
- Require explicit human approval for a novel accounting-perimeter decision.

### E. Validate

- Run accounting identities, period consistency, unit/scale, sign, duplicate, restatement, split and cross-statement checks.
- Compare standardized output with the as-reported filing structure.
- Fail closed: a failed or inconclusive check creates a hold or reasoned blank.
- Record the check version and result; a green pipeline job alone is not evidence that values are correct.

### F. Verify

- An independent verifier opens original filings for risk-based samples.
- Samples cover companies, industries, forms, amendments, taxonomy eras and unusual mappings.
- Any wrong shown value fails the batch and creates a reproducible defect class.
- Fix the root class and replay history; do not patch only the sampled company.

### G. Release

- Value-changing releases require a dry run, diff, flag, rollback and certification result.
- Start with one company, then controlled batches, then cohort-wide activation.
- Monitor wrong-value findings, reasonless blanks, freshness and held cells after release.

### H. Learn

- Convert verified exceptions into versioned rules, tag cards, filing lessons or company-era records.
- Search existing knowledge before opening broad historical documentation.
- Retire or supersede stale knowledge; canonical evidence always wins over summaries.

## 4. Cell contract

Every user-visible financial cell must have exactly one state:

- `reported`: direct authoritative fact selected by a valid mapping.
- `derived`: permitted formula with visible inputs and rule version.
- `estimated`: separately labelled non-filing estimate; never presented as reported actual.
- `preliminary`: company release or 8-K value awaiting formal reconciliation.
- `restated`: later filing changed the previously available value.
- `not_applicable`: the metric does not economically apply, with evidence.
- `not_reported`: applicable but absent from authoritative sources checked.
- `held`: evidence exists but a format change, conflict or failed validation prevents publication.

`null` without one of these reasons is a product defect.

## 5. Definition of done for a metric family

A metric is not complete merely because its parser runs. It is complete only when:

- Its accounting definition and industry applicability are approved.
- Reported, standardized and derived forms are distinguishable.
- Source and mapping lineage reach the original filing.
- Company/era exceptions are versioned rather than hard-coded anonymously.
- Required invariants and failure reasons exist.
- Historical replay is deterministic and idempotent.
- An independent filing sample has zero wrong displayed values.
- Dry-run impact, rollback and production monitoring are documented.
- Coverage, reasoned blanks, held cells and observed error rate are measured.
- A new filing can refresh the metric within the declared freshness target.

## 6. Company certification contract

A company earns a certified state only for a named metric set and as-of filing date. Certification expires or moves to review when:

- A new 10-K, 10-Q or amendment arrives.
- Its statement fingerprint changes.
- A mapping, definition, parser or derivation version changes.
- An invariant or monitoring check fails.
- A related defect class is discovered elsewhere.

The badge must disclose scope, evidence date and observed verification result. It must never imply that every possible company datum is correct.

## 7. Moat scorecard

The Head of Data Product reports these measures; activity counts are secondary.

| Dimension | Core measure | Desired direction |
|---|---|---|
| Trust | Wrong displayed values per 1,000 filing-checked cells | Toward zero, sample size published |
| Certification | Companies certified for the declared metric set | Increasing |
| Completeness | Reasonless blanks | Zero |
| Explainability | Displayed cells with complete provenance | 100% |
| Freshness | Filing accepted to certified display | Decreasing, by company tier |
| Stability | Certified cells invalidated by a later defect | Toward zero |
| Learning | Repeated defects already covered by a reusable rule | Increasing |
| Efficiency | Human reviews per newly certified 1,000 cells | Decreasing without lowering quality |
| History | Point-in-time observations preserving original and restated states | Increasing |
| User trust | Use of “why this number,” correction and provenance features | Increasing |

No team may improve coverage or speed by hiding a decline in verification quality.

## 8. Prioritization rule

Rank data work by:

`user decision value × affected companies × defect severity × recurrence ÷ cost to verify`

Then apply these constraints:

1. Fix wrong displayed values before adding optional metrics.
2. Fix a root-cause class before a one-company exception when both are possible.
3. Deepen the certified top-1,000 cohort before expanding the universe.
4. Prefer work that creates reusable evidence, rules or verification machinery.
5. Stop experiments that cannot state a production decision and measurable kill criterion.

## 9. Team responsibilities

- **Head of Data Product:** user value, metric priority, trust experience and scorecard.
- **Data Chief:** dependency order, defect-class selection and release tier.
- **Standardization Lead:** canonical meaning and perimeter proposals.
- **Tag Expert / Mapper:** tag behavior, structure evidence and scoped mapping proposals.
- **Sector Analyst:** applicability and industry templates.
- **Period Engineer:** periods, quarters, vintages, restatements and splits.
- **Data Engineer:** reliable ingestion, versioned storage, replay and observability.
- **Verifier:** independent filing checks and batch pass/fail.
- **Release Manager:** diff, tests, controlled release and rollback readiness.

No role may approve its own value-changing output.

## 10. Anti-patterns to reject

- Treating a matching label or taxonomy definition as proof of economic equivalence.
- One global tag list applied across every company and era.
- Filling blanks from a vendor without filing reconciliation.
- Deriving EPS or other prohibited values because arithmetic appears possible.
- Overwriting restatements or losing the value known at an earlier date.
- Measuring success by rows ingested, tags mapped, documents written or jobs completed.
- Creating a new plan or status document when a canonical one exists.
- Using an LLM conclusion as accounting evidence.
- Passing a batch because averages look good while individual wrong values remain.
- Expanding to all US stocks before the top-1,000 system is repeatably certified.

## 11. Build sequence

1. Certify one company end to end and expose provenance.
2. Certify controlled batches of 10 across different industry profiles.
3. Complete the highest-decision-value metric families for the top 1,000.
4. Automate fingerprint holds, replay, verification sampling and certification renewal.
5. Publish the quality scorecard and correction history.
6. Expand history, metrics and company coverage only when quality and freshness remain inside their gates.
7. Add direct-company or licensed sources where public filings cannot deliver required frequency or history.

## 12. External benchmark principles

Public materials from established providers support four practices Scrooner should match: retain as-reported and standardized views, use industry-specific templates, preserve point-in-time versions, and combine automated checks with focused quality review.

- Morningstar Equity Data: https://advisor.morningstar.com/Enterprise/VTC/EquityData/EquityDataFeedsFinancialsGuidance.pdf
- FactSet Fundamentals: https://insight.factset.com/resources/at-a-glance-factset-fundamental-datafeed
- LSEG as-reported fundamentals: https://www.lseg.com/en/data-catalogue/company-data/company-fundamentals/fundamentals-as-reported
- S&P Global machine-readable filings: https://www.spglobal.com/market-intelligence/en/news-insights/research/leveraging-machine-readable-filings-to-uncover-valuable-investment-insights

These are evidence about industry practice, not proof of the providers' undisclosed internal pipelines.

## 13. Decision test

Before approving any data initiative, answer:

1. Which investor decision improves?
2. What authoritative evidence supports the output?
3. What new reusable asset will remain after the task?
4. How can the output be wrong, and which check detects each failure?
5. Who verifies it independently?
6. What is withheld when evidence is inconclusive?
7. Which scorecard measure moves, from what baseline to what target?
8. How is the change rolled back?

If these questions cannot be answered, the work is research—not production moat work.
