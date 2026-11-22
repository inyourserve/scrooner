# Pattern P08: derived values without one-filing parts
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Found 2026-11-22 by the verifier. Registry: `patterns.csv` P08. Hits: `pattern_hits.csv` P08.

**What.** A shown DERIVED cell (export class DERIVED, or a `derived:` badge) is exported with no parts, with parts citing more than one filing, or with a part that has no accession or R page. The reader cannot trace the computation to one filing. Doc 02 requires one filing per derivation, with every part printed. Examples: GOOG, GILD, WMT and AMZN gross_profit; ORCL and WMT total_liabilities (derived_cells, value_source canonical_fact).

**How to detect.** `pattern_detectors.p08_derived_parts` on the export. On the resolver it also flags a served `derived_not_printed` row whose nodes are missing or off the printed pages.

**Rule.** `display_cert.check_badges` already fails a multi-filing derived badge, and the gate fails a part with no page. Open: the export of `derived_cells` cells (gross profit = revenue - cost of revenue; total liabilities = assets - total equity incl. NCI - temporary equity) must write their parts as `Tag=value@accession#R` from one filing, as `structural_direct.derived_value` does.

**Examples.** GILD gross_profit FY2015-25 (certified company, so the certificate's derived census checks the identity but the export carries no parts).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 0 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

No element named in this card has a data point, ruling, served cell or known problem in the library.
<!-- END GENERATED: tag library rows -->
