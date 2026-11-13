# Tag-expert review of reader fix files, 2026-11-13

Scope: all 44 `*-fixes-2026-11-13.csv` files on `origin/main` and on `work/reads/redcells-21-40` and `work/reads/redcells-41-60`, as of this commit. Each error is one line in `REVIEW-tag-expert-2026-11-13.csv`.

| Check | Rows | Result |
|---|---|---|
| mapped/component_sum value ties to FSN (undimensioned, same accession, period ±7 days; tolerance by the printed unit) | 1,136 | 1,136 tie |
| AAPL FY2026 rows from 0000320193-26-000026 (not in FSN yet), checked against the sec.gov instance | 40 | 40 tie |
| Member-based tags (not checked) | 4 | not checked |
| Ruling checks: dei cover count as shares; accretion tag as D&A; net interest line mapped; NCI/preferred as dividends; InterestPaid while InterestPaidNet is reported (DQC_0065); G&A alone while S&M is printed | all rows | 0 violations |
| `not_presented` while a 10-K prints an undimensioned, non-coregistrant fact for that period (standard tag for the data point plus every tag named in the note) | 439 | **3 errors** (C deposits, C loans_net, AXP deposits; all 2024-12-31) |

Limit: the `not_presented` check only sees standard tags and the tags named in the note. A company that prints the line under another tag or a custom tag is not caught.
