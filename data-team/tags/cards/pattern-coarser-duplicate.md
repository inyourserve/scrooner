# Pattern P02: one figure tagged twice at different decimals, coarser one served
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Found 2026-11-22 by the verifier (WMT). Registry: `data-team/tags/library/patterns.csv` P02. Hits: `pattern_hits.csv` P02.

**What.** A filer tags the same figure twice in one filing, once as printed on the face and once rounded in a note. WMT FY2023 10-K: `ShortTermBorrowings` is 372,000,000 (dcml -6, face) and 400,000,000 (dcml -8, note), for the same instant, undimensioned. The finer fact is the printed figure and must win.

**How to detect.** `pattern_detectors.p02_coarser_duplicate` (FSN, `--live`). FSN facts are grouped by filing, tag, date and qtrs, keeping undimensioned groups with two or more distinct values. A served resolver node or a shown export part is a hit when its value is the coarser fact, and the finer fact rounds to it at the coarser precision. Two genuinely different figures, where one does not round to the other, are not a hit.

**Rule.** `display_cert` picks the most precise fact (4bf4f69e). In the resolver, X116 covers amortization only. Open for .90: every node pick prefers the highest-dcml duplicate of the same filing, tag and period.

**Examples.** WMT total_debt FY2023 (now served at 372M; the detector guards against regressions).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.94). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.94. 1 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `ShortTermBorrowings`
- **Meaning:** Short-Term Debt (us-gaap, instant, credit). Reflects the total carrying amount as of the balance sheet date of debt having initial terms less than one year or the normal operating cycle, if longer.
- **Data point definition:** total_debt: Total debt: short- and long-term borrowings incl. current portion, commercial paper, finance and capital leases (face or notes), financing obligations and failed sale-leasebacks;  excludes operating leases and accrued interest.
- **Data point:** total_debt
- **Rules:** none
- **Evidence:** 36 companies, 261 served, 13 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseShortTermBorrowings@2021; PostconfirmationShortTermBorrowings@2021; PreconfirmationShortTermBorrowings@2021
<!-- END GENERATED: tag library rows -->
