# Verify: capex fills v18 and cash v1 (origin/work/cash-flow/da-capex f598b9c), 2026-11-03 (PARTIAL: cash v1 stopped at the disk floor)

Seed 20261103. Evidence class: FILING-CHECKED (cash-flow and balance-sheet R pages). Verifier 2 (scrooner-bc).

## Capex fills v18 (10 cells): NO
- BXP Q1 2023 = Construction in progress (119,682) + Building and other capital improvements (39,100) = 158,782K. Right per the v17 finding. Perimeter note: "Tenant improvements" (67,175K) is also capitalized building spend and is excluded; a founder or Standardization call.
- **Wrong: BAM 6M 2024 publishes 127M from a member labelled "Other assets"** (not a capex line).
- Right: MTB 9M 2022 126,810K; ETR 6M 2024 2,124,279K and Q1 2019 951,629K; ES FY2021 3,175,080K and Q1 2022 764,594K; SNA FY2023 95M; IBKR Q1 2019 26M and FY2016 27M.

## Cash v1: incomplete
4 of 4 differences read so far are right. In each, the slot is the pure balance-sheet cash line and production carries the restricted-inclusive total:
- MTCH 2017-12-31: 1,630,809K (production 1,633,682K);
- AAL 2024-12-31: "Cash" 804M; restricted cash and short-term investments printed separately (production 902M = cash flow cash and restricted cash);
- AMT 2017-09-30: 799,467K (production 954.7M = with restricted 155,208K);
- IFF 2020-06-30: 497,412K (production 512M), face not yet read.
The remaining 6 differences, 5 fills and 3 bank ties wait for disk above the 4 GB floor (SecClient stopped at 3.9 GB free).

SEC requests: 30.
