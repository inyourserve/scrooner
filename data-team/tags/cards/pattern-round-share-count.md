# Pattern P04: undimensioned share count that is an exact multiple of 100M

Found 2026-11-22 by the verifier (DIS). Registry: `patterns.csv` P04. Hits: `pattern_hits.csv` P04.

**What.** An undimensioned share count is an exact multiple of 100,000,000, such as DIS `CommonStockSharesOutstanding` 1,800,000,000. It is a cover-page or note figure rounded to hundreds of millions, not the count the statements print.

**How to detect.** `pattern_detectors.p04_round_share_count`. A served weighted basic, weighted diluted or shares outstanding row is a hit when one of its undimensioned nodes is a positive multiple of 10^8. A true count can be round by chance (about 1 in 100 at a 1M printed scale), so check each hit against the face or the equity statement.

**Rule.** RULEBOOK X111 covers shares_outstanding: the equity statement's count from the same filing wins. Weighted counts have no rule yet (open for .90): a weighted count that is a multiple of 10^8 loses to the EPS note's count from the same filing when that note prints a finer one.

**Examples.** BMY shares_outstanding (CommonStockSharesIssued 2.2B), GLW, AMZN weighted diluted FY2018.
