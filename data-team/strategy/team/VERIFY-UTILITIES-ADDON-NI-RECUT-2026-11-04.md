# Verify: utilities income-statement add-on and NI release 1 re-cut (origin/work/income-statement/slot-records 0ac83ec), 2026-11-04

Seed 20261104. Files: release_is_utilities_addon_1/CELL_LIST.csv (revenue 518 + NI 416, 9 CIKs) and release_is_net_income_1/is_net_income_release1_cells.jsonl (903). Evidence class: FILING-CHECKED (income statement R pages). Verifier 2 (scrooner-bc).

## Result
- **Utilities add-on: YES.** Revenue 7 of 7 readable right; SRE FY2021 not read (the kit picked the SDG&E page in the combined filing). NI 8 of 8 right.
- **NI release 1 re-cut: NO (2 cells).** ELS and 1415404 are absent. **PG&E Corp (CIK 1004980) is still in the release:**
  - FY2024 slot 2,512M and FY2025 slot 2,703M (ProfitLoss, gate G1b).
  - The face (10-K 0001004980-26-000009) prints "Net Income" 2,703 / 2,512 and below it "Preferred stock dividend requirement" 110 / 37.
  - The parent's figure is 2,593M / 2,475M (production's value), so ProfitLoss is not the parent's net income here.
  - Under the G1b fix these two cells must hold, as for the 154 filings already moved.

| Set | Ticker | Period | Gate | Value | Face |
|---|---|---|---|---|---|
| revenue | SRE | FY2025 | G1 | 13,702M | Total revenues 13,702 |
| revenue | CMS | Q3 2019 | G1 | 1,546M | Operating Revenue 1,546 (CMS block) |
| revenue | AEE | Q1 2018 | G1 | 1,585M | Total operating revenues 1,585 (Ameren block) |
| revenue | AEE | 6M 2026 | G1 | 4,268M | Operating Revenues 4,268 |
| revenue | CTVA | 9M 2025 | G1 | 13,491M | Net Sales 13,491 |
| revenue | ETR | Q2 2020 | G1 | 2,412,788K | Revenue (Entergy block) 2,412,788 |
| revenue | CMS | Q1 2024 | G1 | 2,176M | Operating Revenue 2,176 |
| revenue | SRE | FY2021 | G1 | 12,857M | not read (wrong page selected) |
| NI | ES | FY2025 | G2b | 1,692,372K | NI 1,699,891 - NCI 7,519 = to common 1,692,372 |
| NI | ETR | FY2019 | G2b | 1,241,226K | 1,258,244 - preferred unit holders 17,018 = 1,241,226 |
| NI | ES | Q3 2024 | G2b | -118,057K | attributable to common (118,057) |
| NI | AEE | FY2024 | G2b | 1,182M | NI 1,187 - NCI 5 = to Ameren common 1,182 |
| NI | AEE | Q3 2016 | G1 | 369M | 371 - NCI 2 = 369 |
| NI | ETR | 9M 2017 | G1 | 890,726K | Earnings applicable to common stock 890,726 |
| NI | TXNM | 9M 2017 | G1 | 134,156K | Net earnings attributable to PNMR 134,156 |
| NI | CMS | FY2017 | G1 | 460M | Available to common 460 |

## Finding for the builder
Remove or hold PG&E Corp (1004980) FY2024 and FY2025 in the NI release (G1b with a printed preferred-dividend line). The re-cut appears to have caught PG&E only under another CIK.

SEC requests: 38.
