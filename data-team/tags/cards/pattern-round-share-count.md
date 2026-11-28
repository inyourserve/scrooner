# Pattern P04: undimensioned share count that is an exact multiple of 100M
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Found 2026-11-22 by the verifier (DIS). Registry: `patterns.csv` P04. Hits: `pattern_hits.csv` P04.

**What.** An undimensioned share count is an exact multiple of 100,000,000, such as DIS `CommonStockSharesOutstanding` 1,800,000,000. It is a cover-page or note figure rounded to hundreds of millions, not the count the statements print.

**How to detect.** `pattern_detectors.p04_round_share_count`. A served weighted basic, weighted diluted or shares outstanding row is a hit when one of its undimensioned nodes is a positive multiple of 10^8. A true count can be round by chance (about 1 in 100 at a 1M printed scale), so check each hit against the face or the equity statement.

**Rule.** RULEBOOK X111 covers shares_outstanding: the equity statement's count from the same filing wins. Weighted counts have no rule yet (open for .90): a weighted count that is a multiple of 10^8 loses to the EPS note's count from the same filing when that note prints a finer one.

**Examples.** BMY shares_outstanding (CommonStockSharesIssued 2.2B), GLW, AMZN weighted diluted FY2018.

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.94). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.94. 2 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `CommonStockSharesOutstanding`
- **Meaning:** Common Stock, Shares, Outstanding (us-gaap, instant). Number of shares of common stock outstanding. Common stock represent the ownership interest in a corporation.
- **Data point definition:** shares_outstanding: Common shares outstanding at period end (all economic classes).
- **Data point:** shares_outstanding; role shares_outstanding:primary#1
- **Rules:** X67; X111; B23; B24; B29; resolver functions DERIVED_YIELDS_TO; comparative_fill; fill_printed_zero_and_comparative; shares
- **Evidence:** 83 companies, 989 served, 2408 proven, 80 certified cells; last verified 2026-11-15
- **Known problems:** pattern P04 round_share_count: 3 open hit(s) at 3 companies, e.g. CVS shares_outstanding 2022-12-31 (resolver) (pattern_hits.csv); pattern P05 comparative_only_year_hidden: 1 open hit(s) at 1 companies, e.g. WFC shares_outstanding 2023-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P04 (3); P05 (1)

### `CommonStockSharesIssued`
- **Meaning:** Common Stock, Shares, Issued (us-gaap, instant). Total number of common shares of an entity that have been sold or granted to shareholders (includes common shares that were issued, repurchased and remain in the treasury). These shares represent capital invested by the firm's shareholders ...
- **Data point definition:** shares_outstanding: Common shares outstanding at period end (all economic classes).
- **Data point:** shares_outstanding
- **Rules:** none
- **Evidence:** 32 companies, 304 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** pattern P04 round_share_count: 17 open hit(s) at 2 companies, e.g. BMY shares_outstanding 2014-12-31 (resolver) (pattern_hits.csv)
- **Pattern hits:** P04 (17)
<!-- END GENERATED: tag library rows -->
