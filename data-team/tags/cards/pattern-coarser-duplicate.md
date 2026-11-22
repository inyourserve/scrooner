# Pattern P02: one figure tagged twice at different decimals, coarser one served

Found 2026-11-22 by the verifier (WMT). Registry: `data-team/tags/library/patterns.csv` P02. Hits: `pattern_hits.csv` P02.

**What.** A filer tags the same figure twice in one filing, once as printed on the face and once rounded in a note. WMT FY2023 10-K: `ShortTermBorrowings` is 372,000,000 (dcml -6, face) and 400,000,000 (dcml -8, note), for the same instant, undimensioned. The finer fact is the printed figure and must win.

**How to detect.** `pattern_detectors.p02_coarser_duplicate` (FSN, `--live`). FSN facts are grouped by filing, tag, date and qtrs, keeping undimensioned groups with two or more distinct values. A served resolver node or a shown export part is a hit when its value is the coarser fact, and the finer fact rounds to it at the coarser precision. Two genuinely different figures, where one does not round to the other, are not a hit.

**Rule.** `display_cert` picks the most precise fact (4bf4f69e). In the resolver, X116 covers amortization only. Open for .90: every node pick prefers the highest-dcml duplicate of the same filing, tag and period.

**Examples.** WMT total_debt FY2023 (now served at 372M; the detector guards against regressions).
