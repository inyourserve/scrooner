# Card family: sector face shapes (what each sector prints, so a blank is a reason, not a miss) — Tag Expert, 2026-11-11
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->
Relay from the certification lead (scrooner-9a), with the Verifier's filing reads (VERIFY-TEMPLATES-AND-LADDER-2026-11-09.md, branch verify/templates-and-ladder-2026-11-09 @ 01d203d; FILING-CHECKED by the Verifier) and the balance-sheet lane (Verifier 9/9).
## Banks (13 of 13 sampled: ASB BAC BNY BOKF BPOP C CBC FHN GBCI JPM MTB PB STT)
- Print interest income and deposits; NOT current totals, gross profit or cost of revenue (unclassified balance sheet: a reason).
- A cost-like line is not cost of revenue: MTB "Other costs of operations" = `OtherNoninterestExpense` (0000036270-26-000010 R5).
- `InterestReceivable` is not accounts receivable (BNY "Accrued interest receivable", 0001390777-26-000033 R6). Combined receivable lines: JPM "Accrued interest and accounts receivable", BAC "Customer and other receivables", BOKF "Receivables": show under their own label.
- Bank opex = the face total noninterest expense (BPOP, C, STT).
- Bank capex: 9 of 13 print "purchases of premises and equipment" (FHN STT BPOP C GBCI BOKF PB BNY CBC).
- Bank total debt: held until a bank perimeter exists (release prep `bank_debt_perimeter_pending`; ZION 548M was partial).
## Brokers and asset managers
- GS, MS, SCHW (SIC 6211) behave like banks (interest income, deposits, repos; no operating income, cost of revenue or current totals). LPLA (6200) prints no operating income. Unclassified balance sheets also at LPL, IBKR, KKR, BX, Ares, T. Rowe, Invesco.
## Card and consumer lenders, homebuilders, others with unclassified balance sheets
- AmEx, Synchrony, Credit Acceptance, OneMain, Affirm; NVR, Lennar, D.R. Horton, Toll, PulteGroup; Deere, CNH, GATX, U-Haul, Rocket, Equitable. No current totals: a reason (balance-sheet lane, Verifier 9/9).
## Insurers
- EQH (SIC 6411) and ACT (Enact, 6411; a mortgage insurer like ESNT and MTG) are insurers despite the SIC: premiums and benefits on the face, no current totals. Operating income printed by 0 of 6 sampled insurers; capex printed by 3 of 6 (MCY, MTG, BRK-A); BRK-A also prints inventory and cost of revenue (industrial arm).
## REITs
- INVH (SIC 6510) and TRNO (6500) are equity REITs outside SIC 6798: real estate at cost and accumulated depreciation, no current totals. AGNC (6798) is a MORTGAGE REIT, but the SIC-6798 template calls it equity_reit: fix the template.
- REIT cost of revenue printed by 1 of 7 (HST). Capex: capital-improvement/development lines (SPG HST BRX INVH, WELL); never property acquisitions. REIT inventory: RYN, LINE, WY; SUI "Inventory of manufactured homes"; WY also prints gross profit.
## Utilities and midstream
- AEE, EIX, CWEN, KMI, LNG: classified balance sheets with operating income. Capitalization-format utilities (NEE, NI, FE, AWK) print long-term debt inside "Total capitalization" after equity: split it (NEE 2020-06-30: L = 12,365 + 25,064 + 42,667 = 80,096M; 0000753308-20-000150).
## Classifier traps (DATA-INFERRED)
- `Deposits` + `InterestIncomeExpenseNet` is not a bank test (FCX ZBRA CPAY WEX). SIC 6199 mixes AXP SYF SOFI (lenders) with 7 crypto/AI miners filing corporate statements (MSTR COIN CRCL IREN HUT WULF BMNR). `bdc_total_investment_income` also fires at insurers.
- Absent-line rule (pilot.is_line_class, branch work/certification-lead/is-absent-lines 87cc6147) treating `InterestIncomeExpenseNet`, `InterestIncomeExpenseNonoperatingNet`, `InterestIncomeExpenseAfterProvisionForLoanLoss` as "net only, never interest expense" and any `InterestExpense*` as interest expense: **CONFIRMED against the interest card**, with two corrections: (1) at banks, total interest expense IS normally printed (`InterestExpenseOperating`/`InterestExpense`: 44 of 44 sampled banks; in my latest-10-K measure only 1 bank lacked it), so a 122-pair "banks with net interest income only" class is mostly older eras or a missing IEO rule, not banks without the line; (2) `InterestExpenseDebt` counts only under the sole-debt rule, and a "…, net" label on an `InterestExpense*` tag is a net perimeter, not gross. Check that `InterestIncomeExpenseOperatingNet` exists in the taxonomy before relying on it.

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.92). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.92. 6 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `InterestExpense`
- **Meaning:** Interest Expense, Operating and Nonoperating (us-gaap, duration, debit). Amount of interest expense classified as operating and nonoperating. Includes, but is not limited to, cost of borrowing accounted for as interest expense.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** interest_expense; other_income_expense_net; operating_expenses; interest_income; polarity interest_expense:positive; role interest_expense:primary#1
- **Rules:** X115; I21; I20; I22; I23; I24; resolver functions resolve_band; family resolve_all.NARROW[interest_expense]
- **Evidence:** 88 companies, 938 served, 24594 proven, 51 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 1 companies, e.g. META interest_expense 2021-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToInterestExpenseNet@2013; CashFlowHedgeGainReclassifiedToInterestExpense@2013; CashFlowHedgeLossReclassifiedToInterestExpense@2013; InterestExpenseRelatedParty@2023

### `InterestIncomeExpenseNet`
- **Meaning:** Interest Income (Expense), Operating (us-gaap, duration, credit). Amount of interest income (expense) classified as operating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+4 more)
- **Data point:** interest_expense; net_interest_income; other_income_expense_net; revenue; interest_income; polarity interest_expense:positive; net_interest_income:signed; role interest_expense:combined#2; net_interest_income:primary#1
- **Rules:** X90; X125; I20; I21; I22; I23; I24
- **Evidence:** 14 companies, 149 served, 686 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InterestRevenueExpense@2012

### `InterestExpenseDebt`
- **Meaning:** Interest Expense, Debt (us-gaap, duration, debit). Amount of the cost of borrowed funds accounted for as interest expense for debt.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_expense; other_income_expense_net; polarity interest_expense:positive; role interest_expense:primary#3
- **Rules:** I20; I21; I22; I23; I24; family resolve_all.NARROW[interest_expense]
- **Evidence:** 10 companies, 113 served, 1434 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DebtInstrumentConvertibleInterestExpense@2013

### `Deposits`
- **Meaning:** Deposits (us-gaap, instant, credit). The aggregate of all deposit liabilities held by the entity, including foreign and domestic, interest and noninterest bearing; may include demand deposits, saving deposits, Negotiable Order of Withdrawal (NOW) and time deposits among others...
- **Data point definition:** deposits: Total deposits at period end. [not applicable: general,lender,broker_am,insurer,equity_reit,utility,bdc]
- **Data point:** deposits; role deposits:primary#1
- **Rules:** none
- **Evidence:** 9 companies, 108 served, 355 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestIncomeExpenseNonoperatingNet`
- **Meaning:** Interest Income (Expense), Nonoperating (us-gaap, duration, credit). Amount of interest income (expense) classified as nonoperating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+1 more)
- **Data point:** interest_expense; interest_income; other_income_expense_net; polarity interest_expense:positive; role interest_expense:combined#1
- **Rules:** I20; I21; I22; I23; I24
- **Evidence:** 9 companies, 21 served, 51 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpenseOperating`
- **Meaning:** Interest Expense, Operating (us-gaap, duration, debit). Amount of interest expense classified as operating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).
- **Data point:** interest_expense; polarity interest_expense:positive; role interest_expense:primary#5
- **Rules:** I20; I21; I22; I23; I24
- **Evidence:** 11 companies, 20 served, 142 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
