# TXN pre-check on the v12 coverage (Ritwik cloud, 2026-11-14): on hold, not a verdict

Dhairya put TXN on hold: certify only on the v13 coverage hash. Before the hold arrived, I found one issue on e14e25e4 (v12) that blocks certification on any proof version unless it is fixed.

**REASON cells do not cite their own period's filing.** All 32 REASON cells (cf_ap_change, shares_outstanding and interest_income, FY2015-2025) cite the FY2025 10-K, 0000097476-26-000059. Only the FY2025 and FY2024 cells can rest on that filing, since it presents both years. FY2015-2023 must each cite their own year's 10-K (or the latest filing that presents that year) and that filing's R page:

| FY | Own 10-K |
|---|---|
| 2015 | 0001564590-16-013126 |
| 2016 | 0001564590-17-002142 |
| 2017 | 0001564590-18-002832 |
| 2018 | 0001564590-19-003839 |
| 2019 | 0000097476-20-000009 |
| 2020 | 0000097476-21-000006 |
| 2021 | 0000097476-22-000009 |
| 2022 | 0000097476-23-000007 |
| 2023 | 0000097476-24-000007 |

Each cited page must show the reason: the combined AP-and-accrued line on the CF, no interest-income line on the IS, or the BS parenthetical printing issued and treasury shares only. The rule is the carry-forward condition agreed on 2026-11-13: a reason from a later filing is not evidence for an earlier period.

Also to check on v13, in the full perimeter sweep: every TXN total_debt year (face short-term debt or commercial paper, finance leases from the lease note, and pre-842 capital leases).

The full draw (32 PROVEN, 5 REASON, all 11 total_debt years) runs on the v13 hash. Its verdict will be written to TXN-certificate-2026-11-14.md (PASS) or TXN-final-draw-2026-11-14.md (FAIL) in this folder.
