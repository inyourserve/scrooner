# Pattern P01: a stated sentence covers several years, the resolver serves fewer

Found 2026-11-22 by the verifier (GILD). Registry row: `data-team/tags/library/patterns.csv` P01. Live hits: `data-team/tags/library/pattern_hits.csv` (pattern_id P01).

**What.** A `text_stated` read quotes a table line or sentence that prints several years side by side, but only the read's own year is served. GILD FY2024 10-K, Other (income) expense note: `Interest income ( 281 ) ( 376 ) ( 106 )`. 281 is served for FY2024. 376 (FY2023) and 106 (FY2022) are printed in the same filing and served nowhere.

**How to detect.** `pattern_detectors.p01_text_stated_years`. In each text_stated quote it finds runs of figures that sit side by side: one table row, or `$1.4 billion, $1.5 billion and $0.6 billion`. Years and labels such as FY2015, R4 and Note 9 end a run, and so do figures separated by words. The row's value anchors the scale. Each other figure in the run is a hit when no served cell of the company equals it within the printed rounding. The year is taken from the column order: own year first, then earlier years.

**Rule (open, resolver .90).** A read whose quote prints a multi-year row serves every year it prints, as a comparative of the quoting filing, under the X109 read contract. The quote, locator and accession are reused, and `quote_period` is set per year. A stated figure never replaces a finer XBRL value (X121, ruling c).

**Examples.** GILD interest_income FY2022-23; GE other_income_expense_net FY2017 and FY2022 (`Other income (Note 18) | 2,259 | 2,126 | 4,140`). Hits on unrelated figures in a quoted row are possible (DELL "DHI Group" counts), so review each hit against the quote before writing a read.
