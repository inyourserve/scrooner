# Verify: interest_expense era rule, 2024+ tags (origin/work/per-share/interest-expense-era adaeb97), 2026-11-02

Seed 20261102. Files: fill.csv (2,287), hold_no_overlap.csv (633). Draw: 3 per (bank / non-bank x quarter / FY) = 12 fills; 5 no_overlap holds. Evidence class: FILING-CHECKED (income statement R page of each accession). Verifier 2 (scrooner-bc).

## Result
- **Fills: YES.** 12 of 12. Each 2024-taxonomy value equals the gross interest expense printed on the face: non-banks "Interest expense" (IEN); banks "Total interest expense" / "Interest expense" (IEO), e.g. Citi FY2025 83,072M, Northern Trust FY2025 6,213.6M.
- **no_overlap holds: right to hold 3 of 5; 2 avoidable.** IRM, CIK 2046386 and CIK 943452 print only "Interest expense, net", so the hold is right. Pinnacle Q1 2026 (Total interest expense 581M) and CIK 1897762 Q3 2025 (Interest expense 81,720K) print a gross line equal to the value, so those holds could fill under the same label check used for fills.

| Set | CIK | Period | Face line | Value | Verdict |
|---|---|---|---|---|---|
| fill | 1489393 | Q1 2025 | Interest expense (107) | 107M | right |
| fill | 66570 | Q1 2026 | Interest expense 7,703 | 7,703K | right |
| fill | 1071739 | Q1 2025 | Interest expense (170) | 170M | right |
| fill | 1288469 | FY2025 | Interest expense (10,056,000) | 10,056K | right |
| fill | 1315098 | FY2025 | Interest expense (41,457) | 41,457K | right |
| fill | 100493 | FY2024 | Interest expense 481 | 481M | right |
| fill (bank) | 36270 | Q1 2026 | Total interest expense 784,000 | 784M | right |
| fill (bank) | 109380 | Q1 2026 | Total interest expense 334 | 334M | right |
| fill (bank) | 22356 | Q1 2026 | Total interest expense 96,667 | 96,667K | right |
| fill (bank) | 73124 | FY2025 | Interest Expense 6,213.6 | 6,213.6M | right |
| fill (bank) | C 831001 | FY2025 | Interest expense 83,072,000 | 83,072M | right |
| fill (bank) | 1281761 | FY2025 | Total interest expense 2,082 | 2,082M | right |
| hold | PNFP 2082866 | Q1 2026 | Total interest expense 581 (gross) | 581M | avoidable |
| hold | 1897762 | Q3 2025 | Interest expense 81,720 (gross) | 81,720K | avoidable |
| hold | IRM 1020569 | Q3 2024 | "Interest Expense, Net (includes interest income ...)" 186,067 | 186,067K | hold right |
| hold | 2046386 | FY2024 | "Interest expense, net" (864); value 1,144M not on face | 1,144M | hold right |
| hold | 943452 | Q1 2026 | "Interest expense, net" (71) | 71M | hold right |

## Findings for the builder
1. no_overlap holds whose face label is the gross line (no "net") and equals the value can fill (Pinnacle, 1897762); keep the net-label holds.

SEC requests: 34.
