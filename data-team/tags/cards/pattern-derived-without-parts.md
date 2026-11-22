# Pattern P08: derived values without one-filing parts

Found 2026-11-22 by the verifier. Registry: `patterns.csv` P08. Hits: `pattern_hits.csv` P08.

**What.** A shown DERIVED cell (export class DERIVED, or a `derived:` badge) is exported with no parts, with parts citing more than one filing, or with a part that has no accession or R page. The reader cannot trace the computation to one filing. Doc 02 requires one filing per derivation, with every part printed. Examples: GOOG, GILD, WMT and AMZN gross_profit; ORCL and WMT total_liabilities (derived_cells, value_source canonical_fact).

**How to detect.** `pattern_detectors.p08_derived_parts` on the export. On the resolver it also flags a served `derived_not_printed` row whose nodes are missing or off the printed pages.

**Rule.** `display_cert.check_badges` already fails a multi-filing derived badge, and the gate fails a part with no page. Open: the export of `derived_cells` cells (gross profit = revenue - cost of revenue; total liabilities = assets - total equity incl. NCI - temporary equity) must write their parts as `Tag=value@accession#R` from one filing, as `structural_direct.derived_value` does.

**Examples.** GILD gross_profit FY2015-25 (certified company, so the certificate's derived census checks the identity but the export carries no parts).
