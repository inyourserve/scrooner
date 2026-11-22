# Pattern P03: share counts off by 10^3 or 10^6

Found 2026-11-22 by the verifier (COP, RTX, SYK). Registry: `patterns.csv` P03. Hits: `pattern_hits.csv` P03, layer `resolver` or `export`.

**What.** A share count is stored at the printed scale ("in thousands" or "in millions") instead of as a number of shares. COP's weighted basic shares are served as 1,241,919 for FY2015, while net income / basic EPS gives about 1.24 billion.

**How to detect.** `pattern_detectors.p03_share_scale`. For each company and period, take net income / basic EPS (skipped when |EPS| < 0.05). A weighted basic, weighted diluted or year-end share count is a hit when its log10 ratio to that figure is within 0.5 of +-3 or +-6. The detector runs on the resolver output and on the shown export. A hit only in `export` means the resolver is fixed but the served value has not been reloaded.

**Rule.** RULEBOOK X114 (resolver .88): the count is scaled by the 10^k that agrees with NI/EPS and flagged `filer_scale_error;share_scale_x<k>`. A remaining export hit needs the flow (structural-load) rerun for the company.

**Examples.** COP weighted_basic/diluted FY2015-19 (export); RTX shares_outstanding (export).
