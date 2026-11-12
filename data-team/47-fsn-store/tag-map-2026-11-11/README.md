# Tag map first pass, top 100 (2026-11-11)

`scrooner-fsn tag-map --library <standard-tag-library.csv>` (fsn_store/tag_map.py, branch work/tag-expert/company-tag-map)
on a LOCAL store built from every SEC FSN set 2014q1-2026m10 for the cohort's top 100 (95 loaded; AMD, XOM, MS, QCOM,
VLO were not in the cohort report used for company ids). Not production: Engineering runs the same read-only command on
the production store to produce the analytics.company_tag_map rows. Library: main @ bca512b8 (453 rows).

- `residue_by_company_top100.csv`: open tag eras per company (rank, ticker), FY2023+ split into extension / standard / detector-held.
- `residue.csv`: every undecided tag era with filing evidence (accession, report, line, label): the Ritwik / Tag Expert queue.
- `library_disagreements.csv`: lines where the company's own structure (rules, detectors) and the library decide differently; structure wins, the Tag Expert reviews.
