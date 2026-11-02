# Tag card: EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations

Written 2026-11-02 by the FSN expert. Family: cash-flow totals (FX effect line).

## Meaning
- **What it is:** the effect of exchange-rate changes on cash, cash equivalents and restricted cash, **including** cash held by disposal groups and discontinued operations.
- **Period type:** duration.
- **Balance:** debit.
- **Taxonomy:** in us-gaap 2025 (`pipeline/scripts/slot_records/results/us_gaap_2025_elements.csv`, branch work/engineering/fsn-pilot).
- **Siblings, all meaning "FX effect on the cash total":**
  - `EffectOfExchangeRateOnCashAndCashEquivalents` (pre-ASU 2016-18, cash only);
  - `EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` (post-ASU 2016-18);
  - `EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsDisposalGroupIncludingDiscontinuedOperations` (a near-twin name; CSCO and RTX print it).

## Who uses it
- Printed on the CF face by **19 EDGAR names in our top-100 extract**, 2018–2026 (297 CF lines; DI, FSN pre):
  - ABT, AMZN, DELL, GEV, GE, GS, MSFT, NEM, ORCL, PM, PLD, QCOM, RTX, TSLA, TMO, DIS.
- The plain post-2018 tag is printed by 80 names, the pre-2018 tag by 87.
- Most common labels: "Effect of exchange rate changes on cash and cash equivalents" (123), "Effect of currency exchange rate changes on cash, cash equivalents…" (44).
- **The label rarely mentions disposal groups.** Read it as the ordinary FX line.

## How it behaves
- It sits exactly where the ordinary FX line sits: a calc child of `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect` with weight +1.
  - MSFT FY2026 10-K 0001193125-26-323660: −210 (FY2024), 63 (FY2025), −196 (FY2026), $M.
  - CFO + CFI + CFF + FX = net change: 11,864 + 63 = 11,927 for FY2025 (DI).
- MSFT switched to it at the FY2022 10-K 0001564590-22-026876 (DI); AMZN in 2024 (pipeline fixture `tests/fixtures/fsn_company_bs/0001018724/pre.tsv` line 251).

## Misuse seen
- `fsn_store/checks.py` `CF_FX` (origin/main b785ec5) lists only the two older siblings.
  - Every column that prints this tag fails the cash-change identity.
  - The FSN pilot (run 41490670432) then blanks MSFT's CFO, dividends and buybacks FY2020–FY2026 as `latest_copy_fails_identity` (22 cells each).
- Proposal: PROPOSALS.md P-1. Treat all four siblings as one FX slot (at most one per column).
