# Primary references and retrieval limits

Last checked in the design discussion: October 17, 2026. Recheck current official documentation when operational decisions depend on changes. No live Scrooner database or repository was inspected while creating these skills.

- SEC API scope and update behavior: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
  Company Facts aggregates non-custom taxonomy facts applying to the whole filing entity; it is not all facts in a filing. Frames align calendar periods approximately; do not use them as issuer fiscal-quarter truth.
- SEC Financial Statement Data Sets: https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets
  Face-statement extracts; quarterly archive buckets are filing buckets, not issuer fiscal-year completeness. December 2024 reprocessing introduced rendering-based selection and a segments field.
- Current dataset schema and join keys: https://www.sec.gov/dera/data/fsds.pdf
  SUB, TAG, NUM, PRE; standard and custom tags. Use tag plus taxonomy/version and filing/context identifiers, not a bare tag join. Inspect the actual header and current documentation; account for segment/coregistrant fields and one-to-many presentation relationships. Deduplicate facts before aggregating joins.
- XBRL duplicate facts: https://www.xbrl.org/WGN/xbrl-duplicates/WGN-2025-01-14/xbrl-duplicates-2025-01-14.html
  Distinguish complete, precision-consistent and inconsistent duplicates; different literals do not necessarily mean conflicting economic facts.
- FASB implementation resources: https://fasb.org/projects/fasb-taxonomies/resources/taxonomy-implementation-guides
  Taxonomy implementation guidance supports tagging interpretation, not universal economic equivalence between similarly named facts.
- Nareit FFO: https://www.reit.com/glossary/funds-operation-ffo
  Preserve the named FFO methodology, reconciliation and shareholder attribution. Do not equate all depreciation or company AFFO variants with Nareit FFO.
- EPS non-additivity example, original issuer filing: https://www.sec.gov/Archives/edgar/data/915389/000091538915000021/R26.htm
  Quarterly EPS need not sum to annual EPS. Never apply a generic flow-subtraction rule to EPS.

## Fact identity and selection
Preserve source-layer identity before defining canonical identity. At minimum investigate issuer, accession, namespace/taxonomy version, tag, context, period start/end or instant, unit, dimensions, consolidation and precision. Never deduplicate solely by company + tag + year. Preserve original occurrences when selecting a product value. Do not sum a parent's total with its components or duplicate presentation occurrences.

Treat tag balance attributes, label similarity, numerical equality and calculation relationships as evidence of limited scope, not standalone proof of canonical equivalence. Calculation relationships may be incomplete; presentation hierarchy is not an accounting equation. A missing relationship is not proof that reported totals are wrong.

## Historical reporting views
Support distinct as-filed/known-at-time and latest-reported/restated views when the product needs them. Preserve the filing's public availability date separately from financial period end and ingestion time. Latest-available values cannot be used in an earlier backtest without a point-in-time policy. Compare compatible reporting bases across periods; do not bridge a reclassification by silently renaming a row.

## Units, signs and attribution
Preserve monetary currency, unit multiplier and raw numeric precision. Use decimal arithmetic for deterministic transformations. Keep source sign and display sign separate. A cash outflow might be reported as a positive magnitude with a subtraction relationship; do not blindly negate every payment tag. Reconcile cash including restricted cash against the matching source cash-flow definition, not an unrelated balance-sheet cash total.

Specify the debt perimeter, treatment of operating/finance leases, cash/investment perimeter, equity attribution and minority interests for every affected metric. Do not silently change these conventions across companies.

## Quarter and TTM rules
Use an explicit additive-concept allowlist; do not classify every duration fact as additive. Require compatible definitions, dates, scope, currency, units and restatement basis before subtracting cumulative flows. Do not generic-subtract EPS, weighted-average shares, ratios, positions or percentages. TTM balance-sheet positions are invalid. Derived TTM flow metrics require compatible non-overlapping periods; ratios use the correct flow/average/point inputs per their formula. Missing any required quarter does not become zero.

## Reason codes
Use clear reason codes such as: MISSING_FILING, SOURCE_NOT_COLLECTED, UNMAPPED_CONCEPT, CONTEXT_MISMATCH, COMBINED_LINE_ONLY, NOT_SEPARATELY_DISCLOSED, NOT_APPLICABLE, NON_ADDITIVE, BASIS_CONFLICT, UNIT_CONFLICT, INCONSISTENT_DUPLICATES, UNSUPPORTED_TEMPLATE, NO_SOURCE_EVIDENCE. Add a new code only when it represents a distinct resolution path.
