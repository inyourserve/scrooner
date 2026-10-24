# Pilot: the first 10 cohort companies, shard findings mapped to root-cause mechanisms (2026-10-24)

Role: Data Verifier. Scope: top-1000 cohort, `shards.csv` rank order from rank 1 (there is no S000 row in shards.csv; S000 is the market-cap audit), excluded rows skipped (AKTX rank 9 ADS ratio, TBLA rank 11 share scale): **NVDA, AAPL, GOOG, MSFT, AMZN, META, AVGO, TSLA, LLY, MU**. Read-only; no DB writes.

**Status: PARTIAL.** Part 1 (map every shard finding to one mechanism) is complete for all 10. Part 2 (round-3 suite dry run) ran for **AAPL, GOOG, MSFT only**. NVDA timed out at the 20s statement cap twice, and AMZN timed out once. The completed companies took 71-87s each against 15-20s on 2026-10-23, and peers were running long `core.fact` scans, so I stopped DB work instead of retrying. NVDA, AMZN, META, AVGO, TSLA, LLY and MU are "suite not run".

## Sources (no filing re-opened for anything the shards or earlier verifier files already proved)
- `doc/data-moat/team/top1000/results/S001.md`: everything **DATA-INFERRED**, because the worker could not reach sec.gov. S002.md (MU) is FILING-CHECKED.
- FILING-CHECKED evidence for the same companies from earlier verifier work:
  - `data-team/35-VERIFIER-GE-AND-HEADLINE-TRIAL-2026-10-21.md`: 111 headline cells at NVDA, AAPL, GOOG, MSFT and AMZN.
  - Ledger rows 49, 64, 65, 70 and 74.
  - The TSLA section of `CERTIFY-HELDOUT-VALIDATION-2026-10-22.md`.
- Filings opened in this pass, only for suite-only findings: AAPL 10-K 0000320193-19-000119 R2 and GOOG 10-Q 0001652044-22-000071 R4.
- Suite: branch `certify-round3` @5382813. One read-only connection, 20s per statement, pooler/app backends at 6 or fewer. Output: `scratchpad/p10/pilot9.json`.

## Mechanism key (status checked against branch heads, 2026-10-24)
| Code | Mechanism | Where | Built? |
|---|---|---|---|
| AUTH | authority gate / 8-K ban + matching-copies dedupe (`source.periodic_form_only@1`, `dedupe.matching_copies@1`) | `work/data-engineer/lane1-stage2e-authority-v2` (4bf20f1, a60a44c) | built on branch, flag OFF, population dry-run not run |
| REV | structural revenue pick | only the RF-13 revenue-total guard (hide) on `lane3-guards` / `lane3-total-debt-rb` | pick not built; guard built |
| SPLIT | share-count / split basis, incl. never deriving per-share | detection: certify r3; RU-1 per-share policy `held/ru1-per-share` (91c6171); split_event re-basing: migrations 0098/0099 schema only | detection + RU-1 built (held); re-basing not built |
| GROUP | group-scoped mapping | `work/sector-analyst/groups-v2.1` (assignment) | assignment built; scoped mapping not built |
| ADS | ADS ratio | NA-15 `mcap.ads_conversion@1` on `lane3-guards` / `rb` | built on branch |
| USD | USD-only check | none found | not built |
| TTM | date-based TTM / growth / staleness / per-share pairing | `lane2-ttm-guards-v2` (`ttm.consecutive_window@1`, `ttm.age_guard@2`), `lane2-w10-anchor` | built on branch, flags OFF |
| NEW-DEBT | total debt from balance-sheet carrying lines | guards R1/R4/R5 on `held/total-debt-guards` and the `lane3-total-debt-rb` family flag (hide only) | hide built; composition not built |
| NEW-SLOT | component/slot composition (D&A = depreciation + amortization; capex variants; extension tags) | none | not built |
| NEW-SHARES | sum dimensioned class / equity-statement share counts | none (P1 primary-filer is a different rule) | not built |
| NEW-VOCAB | single-tag vocabulary gaps (InterestIncomeOther, OtherNonoperatingIncomeExpense, IncreaseDecreaseInReceivables, ...) after coexistence | Tag Mapper queue | not built |
| NEW-DISPLAY | show the resolved or derivable value instead of a blank base row (gross_profit, total_liabilities = L&SE - equity) | none | not built |
| NEW-REASON | visible reason for a legitimate blank (no subtotal, no dividend, universal non-applicable rows) | reason store, migration 0100 (`lane2-base`) | store built; reason rules not built |
| NEW-ID | predecessor/successor CIK history link | none | not built |
| NEW-LINEAGE | market cap must carry source fact ids | none | not built |

## Per-company tables
Columns: cell, shard (or verifier) finding with evidence label, root cause, mechanism, status, and whether the round-3 suite caught it (Y / N / not run).

### NVDA (rank 1), suite not run (20s timeout twice)
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| shares_outstanding Q2 FY27 | missing; page shows 24,304M (Jan) vs filed 24,147M (FC, data-team/35: 10-Q R5 equity-statement column) | count filed only on a dimensioned equity column | NEW-SHARES | not built | not run |
| per-share history around the 2021 4:1 and 2024 10:1 splits | duration-context split missed; 2021 split counted twice (FC, ledger row 65) | split basis | SPLIT | detection built (r2/r3); re-basing not built | not run |
| total_debt base vs resolved | 34,366 vs 33,366 (DI) | LongTermDebt + DebtCurrent possible double count | NEW-DEBT | hide built | not run |
| fcf_growth_5y_cagr | blank: FY2021 capex tag not identified (DI) | vocabulary | NEW-VOCAB | not built | not run |
| market_cap input | filer-rounded 24.1B cover count (FC, informational) | precision of the filed input | none (accepted) | - | - |
| bdc, net_lease, collab revenue, employee_count | blank, no reason (DI) | universal rows lack applicability / reason | NEW-REASON | store built | not run |

### AAPL (rank 2), suite run
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| total_debt Q3 FY26 | 84,297 vs balance sheet 84,344 (FC, data-team/35) | rounded narrative LongTermDebt preferred over split lines | NEW-DEBT | hide built | **N** (no debt finding) |
| diluted_eps Q4 FY25 | 1.84 derived vs 1.85 filed (FC, data-team/35) | per-share derived by subtraction | SPLIT (RU-1) | built (held) | Y (per_share_derived, 10 cells) |
| shares_outstanding 2015-2020 | never re-based for the 2020 4:1 split (FC, ledger row 65) | split basis | SPLIT | detection built; re-base not built | Y (45 cells) |
| **suite-only:** FY2018 diluted/basic EPS 11.91/12.01, Q1-Q3 FY2019 EPS, FY2018 DPS 2.72 | stored as filed before the 2020 split; today's basis /4 (FC: 10-K 0000320193-19-000119 R2 shows 11.91) | split basis | SPLIT | re-base not built | Y (9 cells; the shards did not report them) |
| interest_income, net_interest_income | blank; only combined InvestmentIncomeInterestAndDividend (DI) | combined line | legitimate absence (combined) | NEW-REASON | not built | n/a |
| 4 universal rows | as NVDA | | NEW-REASON | store built | n/a |

### GOOG (rank 3), suite run
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| total_debt FY2025 | 49,085 face vs 48,543 carrying (FC, data-team/35) | face-value LongTermDebt | NEW-DEBT | hide built | **N** |
| EPS 2015-2021 | divided by 400: the 20:1 split is recorded twice (FC, ledger row 74) | split recorded twice | SPLIT | detection built; fix not built | Y (split_ratio_counted_twice + 68 EPS cells) |
| **suite-only:** Q2 2022 diluted EPS 0.0605 | filed 1.21 after the split already applied (FC: 10-Q 0001652044-22-000071 R4); stored divided by 20 again | adjusted though filed after the split | SPLIT | not built | Y |
| buybacks H1-2025 | 28,706 vs 28,306, both non-authoritative, so Q2/Q3 2025 and TTM are blank (DI; ledger row 81 shows the 2026 10-Q prints 28,306 as the comparative) | restated comparative: two periodic copies disagree, no precedence | AUTH (latest periodic precedence) | not built (Stage 2e only drops non-periodic copies) | N |
| D&A, EBITDA x5 | blank: only `Depreciation` filed (DI) | component-only D&A | NEW-SLOT | not built | N |
| gross_profit base, margin_expanding_3yr | base blank, resolved exists (DI) | display reads base row | NEW-DISPLAY | not built | N |
| operating_expenses | CostsAndExpenses includes cost of revenue (DI) | definition | NEW-DISPLAY (derived opex, proposal) | not built | N |
| interest_income x2 | InterestIncomeOther only (DI) | vocabulary | NEW-VOCAB | not built | N |
| dps_growth_3y_cagr | dividends started 2024 | legitimate absence (DI) | NEW-REASON | store built | n/a |

### MSFT (rank 4), suite run
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| diluted_eps Q4 FY26 | 4.80 derived vs 4.81 filed (FC, data-team/35) | per-share derived | SPLIT (RU-1) | built (held) | Y (12 EPS + 10 tax-rate cells) |
| FY2016 net income / operating income | ASC 606 restated FY next to ASC 605 quarters; growth 68% (FC, ledger row 64) | cross-vintage basis | TTM (same-vintage growth) | not built as a fix; detected | Y (review quarters_vs_year_basis_mix) |
| D&A, EBITDA x5 | blank: CF line on an extension tag (DI) | extension tag not read | NEW-SLOT | not built | N |
| interest_income x2 | combined only (DI) | combined line | legitimate absence (combined) | NEW-REASON | not built |
| 4 universal rows | | | NEW-REASON | store built | n/a |

### AMZN (rank 5), suite not run (timeout)
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| total_debt FY2025 and Q2 2026 | 69,291 vs 68,851; 133,320 vs 132,549 (FC, data-team/35) | face-value LongTermDebt | NEW-DEBT | hide built | not run |
| 11 dividend cells | blank, no reason (DI) | pays no dividend | legitimate absence | NEW-REASON | not built |
| research_and_development x2 | no R&D face line (DI) | not presented | legitimate absence | NEW-REASON | not built |
| total_liabilities | derivable as L&SE - equity (DI) | no Liabilities tag | NEW-DISPLAY | not built | not run |

### META (rank 6), suite not run
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| shares_outstanding + 8 dependants | blank: only class-dimensioned counts (DI) | multi-class dimensioned | NEW-SHARES | not built | not run |
| market_cap | value with NULL source_fact_ids (DI) | lineage not enforced | NEW-LINEAGE | not built | not run |
| gross_profit, operating_expenses | as GOOG (DI) | | NEW-DISPLAY | not built | not run |
| inventory x5 | no inventory line (DI) | not applicable | legitimate absence | NEW-REASON | not built |
| dps_growth_3y, peg_ratio | dividends from 2024; non-positive growth (DI) | legitimate | NEW-REASON | store built | n/a |

### AVGO (rank 7), suite not run
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| D&A, EBITDA x5 | Depreciation + AmortizationOfIntangibleAssets filed separately (DI) | component-only D&A | NEW-SLOT | not built | not run |
| interest_income x2, other_income_expense_net | InterestIncomeOther / OtherNonoperatingIncomeExpense (DI) | vocabulary / definition | NEW-VOCAB | not built | not run |
| 10y CAGRs x3 | FY2016 under the predecessor CIK (DI) | registrant cut | NEW-ID (or NEW-REASON) | not built | not run |
| total_debt base 61,671 vs combined 61,079 (DI) | | double count suspect | NEW-DEBT | hide built | not run |

### TSLA (rank 8), round-3 suite not run (round 2 ran on 2026-10-22)
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| diluted EPS 2015-2016 (six cells) | stored as filed; today's basis /15 (FC, CERTIFY-HELDOUT 2026-10-22 section 4) | split basis | SPLIT | re-base not built | Y in round 2 (round 3 per author, DI) |
| dividends x10, buybacks x4, cash returned | blank (DI) | no dividends or repurchases | legitimate absence (needs FC) | NEW-REASON | not built |
| other_income_expense_net | OtherNonoperatingIncomeExpense (DI) | vocabulary | NEW-VOCAB | not built | not run |
| total_debt base 7,721 + 1,340 (DI) | | double count suspect | NEW-DEBT | hide built | not run |
| operating income Q3/Q4 2025 vs yfinance | GAAP figure; vendor definition differs | not wrong | - | - | - |

### LLY (rank 10), suite not run
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| operating_income + 6 dependants | no operating subtotal on the face (DI); shown reason `pre_revenue_biotech_pharma` is wrong (revenue 65,179M) | no subtotal: a legitimate blank with a wrong reason | NEW-REASON | not built | not run |
| capex, FCF x4 | PaymentsToAcquireOtherPropertyPlantAndEquipment unmapped (DI) | capex variant | NEW-SLOT | not built | not run |
| CFO, buybacks Q1/H1 2025; FY2024 balance sheet | 1,665.6 vs 1,666 copies non-authoritative, so values are blank (DI) | precision-consistent duplicates | AUTH (`dedupe.matching_copies@1`) | built on branch | not run |
| total_debt base 7,050 (DebtCurrent only) (DI) | | composition | NEW-DEBT | hide built | not run |
| operating_margin "latest" FY2019 (DI) | stale value shown as latest | staleness | TTM (age guard) | built on branch | not run |
| book_value_per_share, net_cash_per_share | cover-date shares never pair with balance-sheet dates (DI) | date pairing | TTM (W10 anchor) | built on branch | not run |
| FY2016 GP / OI from the Elanco recast 8-K mixed with original COGS (FC, ledger row 70) | 8-K basis mix | | AUTH (8-K ban) | built on branch | not run |
| total_liabilities | current + noncurrent derivable (DI) | | NEW-DISPLAY | not built | not run |
| cf_ap_change, cf_ar_change | combined lines | legitimate absence | NEW-REASON | not built | n/a |

### MU (rank 12; rank 11 TBLA excluded), suite not run
| Cell | Finding | Root cause | Mechanism | Status | Suite |
|---|---|---|---|---|---|
| total_debt_resolved FY2026 | 2,792 vs face 491 + 4,688 = 5,179 (FC, S002 W5, 10-K 0000723125-26-000023 R4) | resolved omits current debt and finance leases | NEW-DEBT | hide built | not run |
| interest_expense / interest_income "latest" | 2024-05 and 2014-02 values shown as current (FC, S002 W9) | stale latest after a tag switch | TTM (age guard) + NEW-VOCAB | guard built on branch; mapping not built | not run |
| cf_ar_change x2, other_income_expense_net | IncreaseDecreaseInReceivables / OtherNonoperatingIncomeExpense unmapped (FC) | vocabulary | NEW-VOCAB | not built | not run |
| accounts_payable + 4 | combined "Accounts payable and accrued expenses" (FC) | legitimate absence (combined); reason correct | - | - | n/a |
| operating_expenses | no total presented (FC) | legitimate absence; reason acceptable | - | - | n/a |

## Roll-up (one row per finding family per company; legitimate absences counted separately)
| Mechanism | Companies (findings) | Built? |
|---|---|---|
| SPLIT (split basis + per-share derivation) | NVDA, AAPL x3, GOOG x2, MSFT, TSLA = 8 | detection and RU-1 built; re-basing not built |
| NEW-DEBT (carrying-line debt) | NVDA, AAPL, GOOG, AMZN, AVGO, TSLA, LLY, MU = 8 | hide guards only |
| NEW-VOCAB | NVDA, GOOG, AVGO, TSLA, MU x2 = 6 | not built |
| NEW-SLOT | GOOG, MSFT, AVGO, LLY = 4 | not built |
| NEW-DISPLAY | GOOG x2, AMZN, META, LLY = 5 | not built |
| NEW-REASON for wrong or missing reasons on non-legitimate rows | LLY (wrong pre_revenue reason), universal rows at all 10 = 11 | store built; rules not built |
| AUTH | GOOG (restated comparative precedence, not built), LLY x2 (matching copies; 8-K ban, built) = 3 | 2 built on branch, 1 not built |
| TTM (staleness, date pairing, same-vintage growth) | MSFT, LLY x2, MU = 4 | built on branch (flags OFF), except the same-vintage growth fix |
| NEW-SHARES | NVDA, META = 2 | not built |
| NEW-ID, NEW-LINEAGE | AVGO, META = 2 | not built |
| REV, GROUP, ADS, USD | 0 in these 10 (ADS hits AKTX rank 9, excluded) | |
| Legitimate absences needing a visible reason | AAPL, MSFT (combined interest); AMZN (no dividend, no R&D); META (inventory; DPS growth; PEG); GOOG (DPS growth); TSLA (no dividend or buyback, needs FC); LLY (no operating subtotal, combined AR/AP); MU (combined AP, no opex total) | NEW-REASON |

**Suite coverage on the three companies that ran (AAPL, GOOG, MSFT):**
- It caught every split-basis and derived-per-share finding the shards and verifiers had (AAPL, GOOG, MSFT).
- It also found 10 wrong values nobody had reported, all FILING-CHECKED: AAPL FY2018/FY2019 EPS and DPS on the pre-split basis, and GOOG Q2 2022 EPS divided twice.
- It missed every total-debt error (AAPL Q3 FY26, GOOG FY2025): 0 debt findings at AAPL and GOOG.
- It missed the D&A and vocabulary blanks, which are blanks rather than values, so I11 territory.

## Next actions
1. Total debt (8 of 10 companies): build the carrying-line composition. The certify suite has no rule for face-value or narrative LongTermDebt, so add a gating check that compares against balance-sheet lines.
2. Split re-basing (8 findings): one re-base pass driven by split_event, plus RU-1 off held, together fix AAPL, GOOG, NVDA and TSLA per-share history.
3. Re-run the suite on NVDA, AMZN, META, AVGO, TSLA, LLY and MU when peer load is lower. At 20s, NVDA cannot be loaded under the current load.
4. Filing-check the DATA-INFERRED S001 findings before their fixes are verified, starting with the shard's own list.
