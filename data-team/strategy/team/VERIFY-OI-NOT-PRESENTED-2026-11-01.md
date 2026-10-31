# Verify: operating income blank reasons (slot.is_operating_income_not_presented@1; origin/work/income-statement/slot-records 2889959, results/release_is_operating_income_2), 2026-11-01

Seed 20261101. Files: is_oi_not_presented_prod_blank_reason_only.jsonl (10,631), is_oi_not_presented_prod_has_value_would_hide.jsonl (2,913) and its Q4 companion (400). Evidence class: FILING-CHECKED (the cell's own accession, the face report named in input_refs). Verifier 2 (scrooner-bc).

## Result
- **Reason-only: YES.** 10 of 10 faces print no operating income line (4 commercial, 3 bank, 3 insurer). The nearest lines are pre-tax income, total costs and expenses, net interest income and underwriting expenses.
- **Would-hide: YES.** 10 of 10 faces print no operating income line, so production's value is derived, not printed. Lennar FY2019: production 2,775,406K; the face prints only total costs and expenses and earnings before income taxes 2,434,292K.
- **Scope note:** the brief asked for "no operating line in any filing for that column". I checked the claimed filing only (one per cell). The package's own stricter check already skips 106 cells where another filing prints the line.

## Cell table
| Stratum | CIK | Period | Shape | Face lines found | Prod | Verdict |
|---|---|---|---|---|---|---|
| reason | GE 40545 | FY2020 | commercial | total costs and expenses; earnings from continuing ops before taxes | blank | right |
| reason | LLY 59478 | 6M 2026 | commercial | income before income taxes only | blank | right |
| reason | 1090012 | FY2018 | commercial | total expenses; earnings before taxes | blank | right |
| reason | 22444 | 6M FY2016 | commercial | total costs and expenses; earnings before taxes | blank | right |
| reason | 1068851 | 6M 2017 | bank | NII; NII after provision; income before taxes | blank | right |
| reason | JPM 19617 | 9M 2023 | bank | NII; total net revenue; income before tax | blank | right |
| reason | 22356 | FY2016 | bank | NII; income before taxes | blank | right |
| reason | 876437 | Q1 2020 | insurer | underwriting and operating expenses; income before tax | blank | right |
| reason | 899051 | Q2 2023 | insurer | "Loss from operations before income tax expense" (a pre-tax line) | blank | right |
| reason | 1095073 | Q3 2019 | insurer | underwriting expenses; income before taxes | blank | right |
| would-hide | LEN 920760 | FY2019 | commercial | total costs and expenses; earnings before taxes 2,434,292K | 2,775,406K | hide right |
| would-hide | LEN 920760 | Q3 FY2019 | commercial | earnings before taxes 667,083K | 759,698K | hide right |
| would-hide | 79879 | Q3 2015 | commercial | income from continuing ops before taxes 581M | 626M | hide right |
| would-hide | RLI 84246 | Q1 2019 | insurer | insurance operating expenses; total expenses; earnings before taxes | 247,153K | hide right |
| would-hide | EVR 1360901 | FY2019 | commercial | net revenues; total expenses; income before taxes | 457,850K | hide right |
| would-hide | 1024478 | Q2 2026 | commercial | income before income taxes 470M | 550M | hide right |
| would-hide | 67887 | Q1 FY2025 | commercial | earnings before taxes 73,579K | 109,051K | hide right |
| would-hide | 79879 | 6M 2023 | commercial | income before taxes 999M | 1,422M | hide right |
| would-hide | FTAI 1590364 | Q3 2017 | bank-shaped | operating expenses; total expenses; loss before taxes | 36,674K | hide right |
| would-hide | AFL 4977 | FY2015 | insurer | total acquisition and operating expenses; earnings before taxes | 4,001M | hide right |

## Findings for the builder
None blocking. Keep the "another filing prints the line" skip (106 cells); it is the only guard for the any-filing condition.

## Requests and disk
SEC requests: 20. No DB access.

## Untested scope
Other filings for the same column; Q4 would-hide stratum (400) not drawn separately; bdc shape (48) not drawn.
