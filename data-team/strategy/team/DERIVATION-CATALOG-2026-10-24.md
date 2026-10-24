# Derivation catalog, top-1000 cohort (Standardization Lead, 2026-10-24). PROPOSAL ONLY

Cohort v1.1 (b13474512c425192), 2015+. Nothing changed. DB reads: read-only, 20s timeout, 6-8 client backends. FC = FILING-CHECKED, DI = DATA-INFERRED.

## 0. Defect: the live A = L + E fallback adds NCI
`mapper/concept_fallback.py` `resolve_balance_sheet_identity_fallback` (f0215f8) computes `assets - equity + adj`; its docstring says `- adj`. NCI is also double counted when equity came from the NCI-inclusive tag.
- WMT 2026-07-31: stored 202,237M, filing 293,914 - 104,506 - 293 = 189,115 (FC, 0000104169-26-000154 R4).
- T 2026-06-30: stored 319,920M, filing 428,359 - 126,434 - 2,005 = 299,920 (FC, 0000732717-26-000297 R5).
- Reach (DI): 5,252 liabilities cells (185 companies; the latest cell at 110), plus 54 equity cells.

## 1. Classes
| # | Class | Fills | Safe when | Invalid when | AC | Proof |
|---|---|---|---|---|---|---|
| D1 | A = L + E | liabilities, equity | L = LiabilitiesAndStockholdersEquity - equity incl. NCI - temporary equity, same instant | equity slot unknown | none | WMT, T (FC) |
| D2 | Face children sum to a total | D&A, capex, debt, shares (issued - treasury) | every child is a face line of one statement and context (slot record) | combined "and other" lines; note-only, custom or dimension-only facts | AC-1, AC-2, AC-5, AC-6 | TXN D&A = Depreciation 1,918 + CapitalizedComputerSoftwareAmortization 81 (FC, 0000097476-26-000059 R7). MSFT custom msft_DepreciationAmortizationAndOther: not derivable (FC, 0001193125-26-323660 R6) |
| D3 | Q4 = FY - 9M; quarter = YTD difference | allowlist flows (RF-27) | same tag, entity and vintage; periodic forms only | per-share, shares, rates, instants (RU-1); mixed vintage; total vs continuing-ops tag (SM 2017, DI) | AC-19, AC-20 | AAPL Q4 FY25 revenue 102,466 = earnings release (FC, 0000320193-25-000077 Ex 99.1). NRG below |
| D4 | Same period from a later comparative | conflicted cells | copy chosen by basis evidence | context shifts (ledger rows 33, 114) | AC-19 | ledger rows 64, 78, 107 |
| D5 | Instant from the next filing's comparative | balance-sheet gaps | same instant; no restatement | entity change (ledger row 82) | AC-19 | ledger |
| D6 | TTM from 4 quarters | TTM metrics | each quarter is a value or a D3 result | balances; a missing quarter counted as 0 | AC-14 | ledger row 10 |
| D7 | Δcash = CFO + CFI + CFF + FX | one missing cash-flow total | restricted-cash-inclusive balance | balance-sheet cash line | AC-21 | WMT FY26 41,565 - 26,350 - 13,553 + 123 = 1,785 = 11,321 - 9,536 (FC, 0000104169-26-000055 R8) |
| D8 | Income-statement identities | gross profit, operating income, opex | already built as `_resolved` concepts | interest inside the costs total (CVX, XOM) | AC-7, AC-9 | ledger rows 20, 58 |
| D9 | Composites (EBITDA, FCF, net debt) | metrics | every input is covered | | AC-1, AC-5, AC-6 | |
| X1 | INVALID: working-capital change from a balance-sheet difference | | never | | | WMT AP: cash flow 1,611 vs balance-sheet change 4,395. AAPL AR 6,682 vs 6,367 (FC, 0000320193-25-000079 R8) |
| X2 | INVALID: shares from WASO; DPS from dividends / shares | | never | | AC-13 | ledger rows 71, 88 |

**NRG 2018 (FC):** the original 9M pretax was 620 (0001013871-18-000039 R2). The 10-K quarterly note is already on the recast basis: Q1-Q3 revenue 7,486, operating income 933 (0001013871-19-000007 R149). That matches the 2019 comparative, which gives pretax 572 (0001013871-19-000035 R2). So Q4 = 467 - 572 = -105. Pairing the earliest copies gives -153.

## 2. Sizing on the residue (latest cells, DI)
| Family | Derivable | Filing read | Absence / state |
|---|---|---|---|
| collaborative_arrangement_revenue 708 | 0 | dimension-only lines | template applicability |
| cf_ap_change 358 | 0 (X1) | ~30 | ~262 combined AP + accrued |
| cf_ar_change 329 | 0 (X1) | ~160 | ~171 broader "receivables": needs a definition |
| other_income_expense_net 275 | after AC-22 (new) | | 202 OtherNonoperatingIncomeExpense (vocabulary) |
| DPS / dividends / dps_growth | 0 (RU-1) | multi-class | non-payers (evidenced_zero) |
| interest_expense 128 | 0 | ~15 | ~45 vocabulary; ~68 net-only (combined) |
| D&A 126 | up to ~85 (D2) | slot check | bank "accretion" lines are combined |
| total_debt 79 | few | | mostly evidenced_zero (AC-4) |
| shares_outstanding 64 | 0 | instance classes | |
| 7,724 pending | 0 (state closures) | | |

History is the big lever. Cohort `period_gap`: 10,173 additive Q4 or quarter cells. Sample of 60 (DI): 40 conflicting, 11 without YTD, 9 clean.

## 3. Order
1. D1 fix: corrects 5,252 wrong values.
2. D3 + D4 vintage pairing: about 6,800 history cells.
3. D2 via the as-filed slot record.
4. D6, D9.

## 4. Stamp
Record state `derived` with:
- `rule_id@version`;
- input fact ids with accession, tag, period and vintage;
- the arithmetic.

Write to `core.derived_fact_input` (0103) and `cell_evidence`. The Verifier re-adds the inputs from the cited R-files and checks the result against a printed total. A derived value never feeds another subtraction.
