# Verify: capex fills v18 and cash v1 (origin/work/cash-flow/da-capex f598b9c), 2026-11-03

Seed 20261103. Evidence class: FILING-CHECKED (cash-flow and balance-sheet R pages). Verifier 2 (scrooner-bc).

## Capex fills v18 (10 cells): NO
- BXP Q1 2023 = Construction in progress (119,682) + Building and other capital improvements (39,100) = 158,782K. Right per the v17 finding. Perimeter note: "Tenant improvements" (67,175K) is also capitalized building spend and is excluded; a founder or Standardization call.
- **Wrong: BAM 6M 2024 publishes 127M from a member labelled "Other assets"** (not a capex line).
- Right: MTB 9M 2022 126,810K; ETR 6M 2024 2,124,279K and Q1 2019 951,629K; ES FY2021 3,175,080K and Q1 2022 764,594K; SNA FY2023 95M; IBKR Q1 2019 26M and FY2016 27M.

## Cash v1: YES
17 of 17 readable cells right (MP 2020-03-31 SPAC-era page not parsed).
- Differences, 9 of 9: each slot is the pure balance-sheet cash line; production carries the cash-flow total including restricted cash. MTCH 1,630,809K vs 1,633,682K; AAL "Cash" 804M vs 902M; AMT 799,467K vs 954.7M; IFF 497,412K vs 511,934K; MRNA 2,623,850K vs 2,635,935K; HLI 1,189,454K vs 1,193,868K; MCD 4,579.3M vs 4,579M (rounding); VFC 659,770K vs 658,485K; CRM 1,606,549K vs 1,607M.
- Fills, 5 of 5: TFX 303,236K; STRL 22,843K; PFGC "Cash" 12.7M (CF cash and restricted 20.0M excluded); TXNM 2,193K (TXNM block); SO 2,009M (CF incl. restricted 2,013M).
- Bank cash-flow ties, 3 of 3: TFC 2015-09-30 cash and due from banks 1,538 + interest-bearing deposits 1,115 + fed funds and resale 127 = 2,780M = CF ending cash; TFC 2020-12-31 5,029 + 13,839 = 18,868M = CF; VLY 2014-12-31 462,569 + 367,838 = 830,407K = CF.
- Also correct: multi-line cells keep only the pure line when cash held in escrow or restricted cash is printed separately (ADC, FRHC, MKL).

SEC requests: 30 (capex) + 45 (cash) + 8 (bank ties).
