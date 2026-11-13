# MSFT approval sample (Ritwik cloud, 2026-11-13)

**Result (corrected 2026-11-14): 32 sampled, 1 error.** The 95% Clopper-Pearson upper bound is 13.98% (one-sided), or 16.22% two-sided. MSFT FAILS the screen until total_debt is fixed and re-sampled.

The error is total_debt FY2016. Served 40,557 = current LTD 0 + LTD 40,557. Under the founder's perimeter (all debt including finance leases), the correct value is 53,461: the FY2017 10-K BS R5 also prints short-term debt of 12,904. My first pass passed this cell because it checked only the proof's own two tags, the same blind spot as the map and the proof. The Verifier found the same error in its sample (98751ede). Method fix: a component-sum cell is now checked against every face line in the data point's perimeter, not only against the tags the proof names.

- **Population:** live `analytics.cell_proof` rows (basis latest, FY and instant at each June 30, FY2015 to FY2026) for MSFT's 46-point template. The template comes from `data-team/companies/reads/MSFT-docmap-2026-11-12.csv`; proofs are keyed on the `_resolved` concept where one exists. Of the 552 cells, 510 are PROVEN and 3 NOT_PRESENTED.
- **Sample:** 32 cells drawn with seed `msft-approval-2026-11-13` (`scripts/approve_sample.py` logic). All 32 are PROVEN cells.
- **Check:** each cell's proof value was compared with the filing's own R page, at the proof's accession, tag and fiscal-year column. Multi-tag cells were compared as the sum of their printed lines.
  - 30 cells were checked by script.
  - 2 were checked by hand because the script misread the page: AR FY2016 and cash FY2016, both 0001193125-16-662209 BS R5.
- **Signs:** capex and buybacks are stored as positive outflows (canonical convention), while the filing prints them negative. The absolute values match.
- **Not yet certified:** MSFT is at 546 of 552 cells (98.9%). The remaining 6 (opex FY2015-17, SG&A FY2016-17, SBC FY2016) are being worked; no certificate is issued until they close.

Per-cell evidence is in `MSFT-approval-sample-2026-11-13.csv`.
