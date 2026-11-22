# Tag cards, ranks 1-95 of TAG-PRIORITY-2026-11-11 (Tag Expert, 2026-11-11)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Worklist: data-team/tags/TAG-PRIORITY-2026-11-11.csv on main (Dhairya; ranked by top-1,000 companies using the tag in FY2023+ filings). One row per tag: the concept (or why it is never one), period type and balance from the taxonomy (`fsn.tag`), the sign convention, the company variants we know, and **when it must NOT map**. Evidence lives in the family cards (interest, revenue, net-income-and-shares, shareholder-returns, debt, capex-and-da, balance-sheet-equity-inventory-other, entity-and-predecessor, operating-income) and the library (`../library/standard-tag-library.csv`). Period: I = instant, D = duration. Balance: D = debit, C = credit.

| Rank | Tag | Cos | Period | Balance | Concept / decision | Sign | Company variants | Do NOT map when |
|---|---|---|---|---|---|---|---|---|
| 1 | LiabilitiesAndStockholdersEquity | 731 | I | C | excluded: identity_check_line (= Assets) | credit, positive | also appears on CF? (BS/CF per worklist) only as a check | never a display cell; use only for identity I-1 |
| 2 | NetCashProvidedByUsedInFinancingActivities | 731 | D | D | cash_flow_financing(_resolved) | debit-typed; stored positive = inflow, negative = outflow | …ContinuingOperations twin at ~40 top-100 names | do not map the continuing twin when the total is printed; never sum both |
| 3 | Assets | 731 | I | D | total_assets_resolved | debit, positive | co-registrant utilities print several Assets rows (PEG R5) | not a pre-merger shell (Assets≈0: MDT 2015, BKR, AMCR…, entity-and-predecessor.md) |
| 4 | NetCashProvidedByUsedInInvestingActivities | 730 | D | D | cash_flow_investing(_resolved) | debit-typed; negative = outflow | …ContinuingOperations twin | as financing |
| 5 | NetCashProvidedByUsedInOperatingActivities | 727 | D | — | cfo_resolved | no balance type in taxonomy; positive = inflow | …ContinuingOperations is the ONLY CFO line at many filers (MSFT FY2014-18) | continuing twin only when no total printed (16 latest 10-Ks print both: AMD 6,493 vs 7,709) |
| 6 | EarningsPerShareDiluted | 718 | D | — | diluted_eps_resolved | per share; negative for losses | multi-class per StatementClassOfStockAxis; CAD at CP; LP-unit tags at partnerships | never derive Q4 (FY−9M); continuing-ops EPS tags only when no EarningsPerShare* and no discontinued per-share line is printed (net-income-and-shares.md §10; VRSN 0001014473-26-000006 R5); never a non-USD unit |
| 7 | EarningsPerShareBasic | 718 | D | — | basic_eps_resolved | as diluted | EarningsPerShareBasicAndDiluted (one line) at some filers | as diluted; old 10-K quarterly tables may carry continuing-ops EPS (HSIC) |
| 8 | AssetsAbstract | 714 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 9 | RetainedEarningsAccumulatedDeficit | 708 | I | C | component of stockholders_equity (equity_component) | credit; negative = accumulated deficit |  | never as equity |
| 10 | IncomeTaxExpenseBenefit | 707 | D | D | income_tax_expense_resolved | debit; negative = benefit | note copies can be a component (ODFL Tax Act 104.9M); comparative sign flips across vintages (CMG FY2018) | not a note component fact; check sign vintage before Q4 derivation |
| 11 | AccumulatedOtherComprehensiveIncomeLossNetOfTax | 694 | I | C | component of stockholders_equity | credit; often negative |  | never as equity or OCI flow |
| 12 | StockholdersEquity | 690 | I | C | stockholders_equity_resolved | credit, positive (negative = deficit) | includes preferred (JPM PSA HIW); CAD at HOVR; BDC net assets; EQ-statement copies | not the EQ statement column (BS is the source; EQ opening can be restated: MSFT 83,090 vs 71,997); not when only the NCI-inclusive total is printed |
| 13 | NetIncomeLoss | 689 | D | C | net_income_resolved (IS); CF/CI start line = identity_check_line | credit; negative = loss | NIACSB is the parent line at ~30 filers; ProfitLoss is a different line (MDT) | never from DEF 14A proxy facts (MA); CF/CI copies are not separate cells |
| 14 | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect | 686 | D | D | excluded: identity_check_line (net change in cash) | debit-typed; signed | pre-ASU 2016-18 CashAndCashEquivalentsPeriodIncreaseDecrease | never a display cell |
| 15 | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | 675 | I | D | excluded: identity_check_line (opening/closing cash incl. restricted) | debit, positive | also on the BS at ~10 names | NOT cash_and_equivalents when the label names restricted cash (combined line, shown under its label); cash only when it is the sole cash line and the label names no restricted cash (FITB 0000035527-26-000202 R2 4,374M) |
| 16 | CommonStockSharesAuthorized | 673 | I | — | excluded: per_share_detail (BS parenthetical) | shares |  | never shares outstanding |
| 17 | CommonStockSharesIssued | 669 | I | — | excluded: per_share_detail; input to issued − treasury | shares | RRC negative treasury under an equity-component member | issued includes treasury: never shares_outstanding alone |
| 18 | NetCashProvidedByUsedInInvestingActivitiesAbstract | 657 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 19 | NetCashProvidedByUsedInFinancingActivitiesAbstract | 657 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 20 | NetCashProvidedByUsedInOperatingActivitiesAbstract | 652 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 21 | CommonStockParOrStatedValuePerShare | 651 | I | — | excluded: per_share_detail | per share | FSDS 4-decimal truncation (0.00001 → 0.0000) | never a value cell |
| 22 | CashAndCashEquivalentsAtCarryingValue | 645 | I | D | cash_and_equivalents_resolved (BS); CF copy = identity line | debit, positive | banks: CashAndDueFromBanks + InterestBearingDepositsInBanks | not the CF closing line when the BS prints it (identity copy) |
| 23 | AdjustmentsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract | 641 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 24 | CommonStockValue | 634 | I | C | component of stockholders_equity | credit | CommonStocksIncludingAdditionalPaidInCapital combined at ~18 | never as equity |
| 25 | LiabilitiesAndStockholdersEquityAbstract | 623 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 26 | IncreaseDecreaseInOperatingCapitalAbstract | 610 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 27 | PaymentsForRepurchaseOfCommonStock | 609 | D | C | share_buybacks_resolved | credit-typed payment; stored positive = outflow | PaymentsForRepurchaseOfEquity second line at 13 of 16 coexisting filers; excise-inclusive customs | not cumulative program-to-date durations (AZO); not withholding or preferred redemptions |
| 28 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | 605 | D | C | income_before_tax_resolved | credit; negative = pre-tax loss | pair with …MinorityInterestAndIncomeLossFromEquityMethodInvestments (MSFT switched Q2 FY2022) | if both printed they differ by equity-method income: check calc |
| 29 | ShareBasedCompensation | 605 | D | D | sbc | debit; CF add-back, positive | AllocatedShareBasedCompensationExpense is the note twin | not "Amortization of stock-based compensation" lines that net other items |
| 30 | WeightedAverageNumberOfDilutedSharesOutstanding | 598 | D | — | weighted_diluted_shares (live since 0122) | shares, duration | scale ×1000 errors (RPAY TBLA) | never shares_outstanding (period-end count) |
| 31 | WeightedAverageNumberOfSharesOutstandingBasic | 597 | D | — | weighted_basic_shares (live since 0122) | shares, duration | …BasicAndDiluted single line | as diluted |
| 32 | AssetsCurrent | 597 | I | D | current_assets_resolved | debit, positive | TXT prints it only for the Manufacturing group (no consolidated total) | unclassified balance sheets (banks, insurers) have none: reason, not a value |
| 33 | LiabilitiesCurrent | 597 | I | C | current_liabilities_resolved | credit, positive |  | as current assets |
| 34 | Goodwill | 593 | I | D | goodwill | debit, positive |  | face line only; not a segment-note fact |
| 35 | OtherAssetsNoncurrent | 570 | I | D | excluded: component_no_concept | debit | label "All other assets" | never a total |
| 36 | PropertyPlantAndEquipmentNet | 569 | I | D | ppe_net_resolved | debit, positive | …AndFinanceLeaseRightOfUseAsset… (incl. finance-lease ROU) at ~25 names | never both; flag the lease-inclusive perimeter |
| 37 | Liabilities | 566 | I | C | total_liabilities_resolved | credit, positive | not printed at 217 of 999 latest 10-Ks: reason not_presented, NEVER derived (doc 02, 2026-11-01 item 4: instants are never derived; corrected 2026-11-11); also used for LESS than total liabilities (LW 0001558370-17-000080, WFRD 0001603923-19-000095, PCAR segment members): check it is the L&E calc child | never from a custom child of Liabilities (release prep dropped that seed) |
| 38 | OperatingIncomeLoss | 559 | D | C | operating_income_resolved | credit; negative = operating loss | PLD custom pre-gains line above it; banks PEBO/BANR mis-tag pretax | never note-sourced (segment totals ELV SLB IP; WPC pretax) |
| 39 | CommitmentsAndContingencies | 554 | I | C | excluded: caption | credit; normally nil |  | never a value |
| 40 | StatementTable | 549 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 41 | StatementLineItems | 549 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 42 | OtherLiabilitiesNoncurrent | 546 | I | C | excluded: component_no_concept | credit |  | never debt or a total |
| 43 | AssetsCurrentAbstract | 540 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 44 | LiabilitiesCurrentAbstract | 539 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 45 | CommonStockSharesOutstanding | 531 | I | — | shares_outstanding_resolved (BS face/parenthetical, at the BS date) | shares, instant | BS parenthetical at 407 of 632 latest 10-Ks; EQ column can be the ISSUED count (PKOH); per class at multi-class filers | not the cover dei count (different date); not the EQ opening row |
| 46 | PaymentsToAcquirePropertyPlantAndEquipment | 529 | D | C | capex_resolved (add a std_tag rule) | credit-typed payment; stored positive | PaymentsToAcquireProductiveAssets (Aptiv incl. software); Air Lease flight equipment | not total capex where other capex lines exist; not the discontinued block (AMD) |
| 47 | StockholdersEquityAbstract | 522 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 48 | PaymentsToAcquireBusinessesNetOfCashAcquired | 492 | D | C | excluded: component_no_concept (acquisitions) | credit-typed payment |  | never capex |
| 49 | AccountsPayableCurrent | 478 | I | C | accounts_payable | credit, positive |  | not AccountsPayableAndAccruedLiabilities (combined) |
| 50 | PaymentsForProceedsFromOtherInvestingActivities | 473 | D | C | excluded: component_no_concept | signed |  | never capex or a total |
| 51 | InterestPaidNet | 473 | D | C | cash_paid_for_interest only when InterestPaid is not printed (label check: XOM operating portion) | credit-typed payment | InterestPaid (gross of capitalised) | never interest_expense |
| 52 | ProceedsFromPaymentsForOtherFinancingActivities | 467 | D | D | excluded: component_no_concept | signed |  | never buybacks/dividends |
| 53 | SupplementalCashFlowInformationAbstract | 465 | — | — | abstract (structure) | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 54 | InterestExpense | 462 | D | D | interest_expense_resolved | debit, positive | banks: pair with InterestExpenseOperating (2024+); DIS 10-K FY value NEGATIVE vs positive 10-Qs | "…, net" label (net of interest income: DAL); DQC_0181 position tests; no Q4 derivation across a sign flip |
| 55 | RevenueFromContractWithCustomerExcludingAssessedTax | 447 | D | C | revenue_sanity_resolved | credit, positive | a COMPONENT next to a Revenues total at 33 latest 10-Ks (GM, WMT, Welltower); larger than the net face total (MA, WMB) | component when a calc child of another revenue line; never a REIT/bank total |
| 56 | ProfitLoss | 446 | D | C | component of net_income (nci_component) | credit | equals NI to parent only with no NCI anywhere (ITW, Terex) | never NI to parent when an NCI line exists |
| 57 | OtherNonoperatingIncomeExpense | 440 | D | C | other_income_expense_net | credit; signed | "Interest and other income (expense), net" labels = combined with interest | never interest |
| 58 | EarningsPerShareAbstract | 438 | — | — | abstract | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 59 | AccountsReceivableNetCurrent | 436 | I | D | accounts_receivable | debit, positive | ReceivablesNetCurrent wider (13 names) | not notes/financing receivables |
| 60 | IntangibleAssetsNetExcludingGoodwill | 415 | I | D | excluded: component_no_concept | debit | FiniteLivedIntangibleAssetsNet alternative | never goodwill |
| 61 | DeferredIncomeTaxExpenseBenefit | 414 | D | D | excluded: component_no_concept (CF adjustment / IS component) | debit; signed |  | never income_tax_expense (total) |
| 62 | InventoryNet | 413 | I | D | inventory | debit, positive | other face totals: FG-only (GAP NKE AZO SYY LULU), …CustomerAdvances (BA LMT), InventoryGross (MKC: double count), RealEstate (Zillow) | not WIP contract assets (OMC); net of a face LIFO reserve (KR) |
| 63 | EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | 408 | D | D | excluded: identity_check_line (FX) | debit-typed; signed | 4 FX siblings incl. …IncludingDisposalGroup… and CSCO's twin | sum every FX-family calc child; never a display cell |
| 64 | DeferredIncomeTaxLiabilitiesNet | 408 | I | C | excluded: component_no_concept | credit |  | never debt |
| 65 | OperatingLeaseRightOfUseAsset | 401 | I | D | excluded: component_no_concept | debit |  | never PP&E (unless the combined PPE+ROU tag is printed) |
| 66 | IncreaseDecreaseInAccountsReceivable | 401 | D | C | cf_ar_change | credit-typed: stored positive = INCREASE in AR = cash outflow, presented negated (AAPL FY2025 prints (6,682), stores +6,682,000,000; 0000320193-25-000079, FILING-CHECKED 2026-11-11, corrected) | IncreaseDecreaseInReceivables (wider); CMI AccountsAndNotes | not combined receivable lines |
| 67 | IncreaseDecreaseInInventories | 397 | D | C | cf_inventory_change | credit-typed: stored positive = INCREASE in inventory = cash outflow (AAPL FY2025 prints 1,400 inflow, stores −1,400,000,000; corrected 2026-11-11) |  | sign convention: never flip |
| 68 | PreferredStockSharesAuthorized | 395 | I | — | excluded: per_share_detail | shares |  | never |
| 69 | DepreciationDepletionAndAmortization | 394 | D | D | depreciation_and_amortization_resolved (CF composition preferred) | debit; positive add-back | HD FY2025+ excludes intangibles; DDA can include financing-cost/DAC amortization | not an IS sub-line (Kura, SBUX); not combined customs (MSFT "…and other") |
| 70 | StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | 391 | I | C | component (total equity incl. NCI; nci_component) | credit | the ONLY equity total at UNH, AT&T, HAS | stockholders_equity only when NO parent line and NO NCI line is printed (JNJ, AVGO, V, QCOM; fsn-balance-sheet-liabilities-equity.md); with an NCI line and no parent line: not_presented, never total − NCI (instants never derived); FE 10-Q small non-face values |
| 71 | PreferredStockValue | 384 | I | C | component of stockholders_equity | credit |  | never common equity |
| 72 | AdditionalPaidInCapitalCommonStock | 380 | I | C | component of stockholders_equity | credit | AdditionalPaidInCapital alternative | never |
| 73 | SellingGeneralAndAdministrativeExpense | 376 | D | D | sga_expense | debit, positive | G&A + S&M printed separately (components) | not when only G&A is printed (that is a component) |
| 74 | CostOfGoodsAndServicesSold | 375 | D | D | cost_of_revenue_resolved | debit, positive | …ExcludingDepreciationDepletionAndAmortization (36: ruling pending) | not CostsAndExpenses; not a single component line (TSLA automotive) |
| 75 | IncomeTaxesPaidNet | 366 | D | C | cash_paid_for_income_taxes (wins when both printed) | credit-typed payment | IncomeTaxesPaid | never income_tax_expense |
| 76 | TreasuryStockCommonShares | 362 | I | — | excluded: per_share_detail; input to issued − treasury | shares |  | never |
| 77 | OperatingLeaseLiabilityNoncurrent | 358 | I | C | excluded: component_no_concept | credit |  | never debt |
| 78 | PreferredStockParOrStatedValuePerShare | 355 | I | — | excluded: per_share_detail | per share |  | never |
| 79 | PreferredStockSharesIssued | 348 | I | — | excluded: per_share_detail | shares |  | never |
| 80 | MinorityInterest | 346 | I | C | component (NCI equity; nci_component) | credit | redeemable NCI is mezzanine (separate tags) | never subtract twice from an NCI-inclusive total |
| 81 | OtherNoncashIncomeExpense | 346 | D | C | excluded: component_no_concept | credit-typed; signed |  | never |
| 82 | LongTermDebtNoncurrent | 341 | I | C | component of total_debt_resolved (debt lane) | credit, positive | pair with LongTermDebtCurrent when no LongTermDebt; capitalization-format utilities print it after equity | not face value; never add LongTermDebt on top |
| 83 | RepaymentsOfLongTermDebt | 336 | D | C | excluded: component_no_concept | credit-typed payment |  | never |
| 84 | PaymentsRelatedToTaxWithholdingForShareBasedCompensation | 331 | D | C | excluded: supplemental (buyback EXCLUSION) | credit-typed payment | labelled "repurchase" at some filers | never share_buybacks (founder perimeter) |
| 85 | NetIncomeLossAttributableToNoncontrollingInterest | 329 | D | D | component (nci_component) | debit-typed; can be negative (CAT −2M) |  | never |
| 86 | ProceedsFromIssuanceOfLongTermDebt | 316 | D | D | excluded: component_no_concept | debit-typed receipt |  | never |
| 87 | PaymentsOfDividendsCommonStock | 310 | D | C | dividends_paid_resolved | credit-typed payment; positive | PaymentsOfDividends (generic), PaymentsOfOrdinaryDividends (PFE JNJ CL) | not NCI/preferred lines |
| 88 | DeferredIncomeTaxAssetsNet | 310 | I | D | excluded: component_no_concept | debit |  | never |
| 89 | InterestExpenseNonoperating | 306 | D | D | interest_expense_resolved | debit, positive | 2024+ taxonomy; MSFT note-only from Q1 FY2025; CAT "excluding Financial Products" | "- net" labels (13 lines) are net; under OperatingExpenses calc = wrong element (DQC_0181) |
| 90 | IncreaseDecreaseInAccountsPayable | 303 | D | D | cf_ap_change | debit-typed: positive = increase = cash inflow |  | not IncreaseDecreaseInAccountsPayableAndAccruedLiabilities (combined) |
| 91 | OtherAssetsCurrent | 302 | I | D | excluded: component_no_concept | debit |  | never |
| 92 | PrepaidExpenseAndOtherAssetsCurrent | 297 | I | D | excluded: component_no_concept | debit |  | never |
| 93 | Revenues | 290 | D | C | revenue_sanity_resolved | credit, positive | bank Revenues can be NET of interest expense (C, BAC, PNC, JPM); "Revenues and other income" (CVX); NTAP/EMR undimensioned note copies | not note copies (segments, acquired targets); total over an RCFC component inside one IS |
| 94 | RevenuesAbstract | 289 | — | — | abstract | — |  | abstract heading: no value ever; structural (leave unmapped with status "abstract") |
| 95 | AdditionalPaidInCapital | 287 | I | C | component of stockholders_equity | credit |  | never |

Covered: 95 of 95 ranks.

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 72 elements named in this card have library knowledge; the 30 most served are below. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `LiabilitiesCurrent`
- **Meaning:** Liabilities, Current (us-gaap, instant, credit). Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
- **Data point definition:** current_liabilities: Total current liabilities as printed on a classified balance sheet. [not applicable: bank,insurer,bdc]; total_liabilities: Total liabilities as printed.
- **Data point:** current_liabilities; total_liabilities
- **Rules:** X39; C03; C09; B01; B04; resolver functions resolve; regions; resolve_family
- **Evidence:** 95 companies, 1439 served, 32338 proven, 137 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCurrentLiabilities@2020; FreshStartAdjustmentIncreaseDecreaseCurrentLiabilities@2021; PostconfirmationCurrentLiabilities@2021; PreconfirmationCurrentLiabilities@2021 (+3 more)

### `WeightedAverageNumberOfSharesOutstandingBasic`
- **Meaning:** Weighted Average Number of Shares Outstanding, Basic (us-gaap, duration). Number of [basic] shares or units, after adjustment for contingently issuable shares or units and other shares or units not deemed outstanding, determined by relating the portion of time within a reporting period that common shares or units...
- **Data point definition:** weighted_basic_shares: Weighted average basic common shares as printed.
- **Data point:** weighted_basic_shares; role weighted_basic_shares:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1316 served, 4583 proven, 139 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000063908-24-000072: MCD FY2023 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average basic shares 727.9;  the XBRL fact is 727.9 shares (scale ; filer XBRL error 0000063908-25-000012: MCD FY2024 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average basic shares 718.3;  the XBRL fact is 718.3 shares (scale  (+4 more)
- **Pattern hits:** P03 (5); P04 (3)
- **Deprecation:** replaces WeightedAverageNumberOfShareOutstandingBasicAndDiluted@2022

### `IncomeTaxExpenseBenefit`
- **Meaning:** Income Tax Expense (Benefit) (us-gaap, duration, debit). Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations.
- **Data point definition:** income_tax_expense: Income tax expense (benefit) for the period, as printed;  a benefit is a real negative.
- **Data point:** income_tax_expense; polarity income_tax_expense:signed; role income_tax_expense:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1302 served, 44905 proven, 140 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces IncomeTaxExpenseBenefitContinuingOperations@2013; RestatementOfPriorYearIncomeTaxEffects@2020

### `EarningsPerShareBasic`
- **Meaning:** Earnings Per Share, Basic (us-gaap, duration). The amount of net income (loss) for the period per each share of common stock or unit outstanding during the reporting period.
- **Data point definition:** basic_eps: Basic EPS per common share as printed (latest print = split-adjusted history, X92).
- **Data point:** basic_eps; role basic_eps:primary#1
- **Rules:** none
- **Evidence:** 109 companies, 1236 served, 4644 proven, 139 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; EarningsPerShareBasicAndDiluted@2022 (+5 more)

### `WeightedAverageNumberOfDilutedSharesOutstanding`
- **Meaning:** Weighted Average Number of Shares Outstanding, Diluted (us-gaap, duration). The average number of shares or units issued and outstanding that are used in calculating diluted EPS or earnings per unit (EPU), determined based on the timing of issuance of shares or units in the period.
- **Data point definition:** weighted_diluted_shares: Weighted average diluted common shares as printed.
- **Data point:** weighted_diluted_shares; role weighted_diluted_shares:primary#1
- **Rules:** none
- **Evidence:** 108 companies, 1234 served, 4539 proven, 139 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000063908-24-000072: MCD FY2023 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average diluted shares 732.3;  the XBRL fact is 732.3 shares (scal; filer XBRL error 0000063908-25-000012: MCD FY2024 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average diluted shares 721.9;  the XBRL fact is 721.9 shares (scal (+4 more)
- **Pattern hits:** P03 (5); P04 (3)
- **Deprecation:** replaces WeightedAverageNumberOfShareOutstandingBasicAndDiluted@2022

### `EarningsPerShareDiluted`
- **Meaning:** Earnings Per Share, Diluted (us-gaap, duration). The amount of net income (loss) for the period available to each share of common stock or common unit outstanding during the reporting period and to each share or unit that would have been outstanding assuming the issuance of common shares ...
- **Data point definition:** diluted_eps: Diluted EPS per common share as printed (latest print, X92).
- **Data point:** diluted_eps; role diluted_eps:primary#1
- **Rules:** none
- **Evidence:** 109 companies, 1233 served, 39141 proven, 139 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; EarningsPerShareBasicAndDiluted@2022 (+5 more)

### `NetIncomeLoss`
- **Meaning:** Net Income (Loss) Attributable to Parent (us-gaap, duration, credit). The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income; role net_income:primary#1
- **Rules:** X77; C29; resolver functions resolve
- **Evidence:** 105 companies, 1212 served, 28185 proven, 129 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InvestmentCompanyNetAssetsFromOperationsIncreaseDecrease@2023; RestatementOfPriorYearIncomeNetOfTax@2020

### `Goodwill`
- **Meaning:** Goodwill (us-gaap, instant, debit). Amount, after accumulated impairment loss, of asset representing future economic benefit arising from other asset acquired in business combination or from joint venture formation or both, that is not individually identified and separately r...
- **Data point definition:** goodwill: Goodwill at period end as printed.
- **Data point:** goodwill; role goodwill:primary#1
- **Rules:** X78; B20
- **Evidence:** 105 companies, 1206 served, 4387 proven, 137 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces BusinessCombinationGoodwillRecognizedSegmentAllocation@2013; FreshStartAdjustmentIncreaseDecreaseGoodwill@2021; FreshStartAdjustmentIncreaseDecreaseReorganizationValueInExcessOfAmountsAllocableToIdentifiableAssets@2021; PostconfirmationGoodwill@2021 (+2 more)

### `StockholdersEquity`
- **Meaning:** Equity, Attributable to Parent (us-gaap, instant, credit). Amount of equity (deficit) attributable to parent. Excludes temporary equity and equity attributable to noncontrolling interest.
- **Data point definition:** stockholders_equity: Equity attributable to the parent at period end.
- **Data point:** stockholders_equity
- **Rules:** X78; C06; resolver functions resolve
- **Evidence:** 104 companies, 1190 served, 22897 proven, 126 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CommonStockholdersEquity@2013; EquityMethodInvestmentSummarizedFinancialInformationEquityOrCapital@2020; FreshStartAdjustmentIncreaseDecreaseStockholdersEquity@2021; PostconfirmationStockholdersEquity@2021 (+1 more)

### `NetCashProvidedByUsedInFinancingActivities`
- **Meaning:** Cash Provided by (Used in) Financing Activity, Including Discontinued Operation (us-gaap, duration, debit). Amount of cash inflow (outflow) from financing activity, including, but not limited to, discontinued operation. Financing activity includes, but is not limited to, obtaining resource from owner and providing return on, and return of, their ...
- **Data point definition:** cash_flow_financing: Net cash provided by (used in) financing activities as printed.
- **Data point:** cash_flow_financing; polarity cash_flow_financing:signed; role cash_flow_financing:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1161 served, 42499 proven, 136 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NetCashProvidedByUsedInInvestingActivities`
- **Meaning:** Cash Provided by (Used in) Investing Activity, Including Discontinued Operation (us-gaap, duration, debit). Amount of cash inflow (outflow) from investing activity, including, but not limited to, discontinued operation. Investing activity includes, but is not limited to, making and collecting loan, acquiring and disposing of debt and equity instr...
- **Data point definition:** cash_flow_investing: Net cash provided by (used in) investing activities as printed.
- **Data point:** cash_flow_investing; polarity cash_flow_investing:signed; role cash_flow_investing:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1161 served, 42135 proven, 136 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CashAndCashEquivalentsAtCarryingValue`
- **Meaning:** Cash and Cash Equivalent (us-gaap, instant, debit). Amount of cash and cash equivalent. Cash includes, but is not limited to, currency on hand, demand deposit with financial institution, and account with general characteristic of demand deposit. Cash equivalent includes, but is not limited t...
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents; role cash_and_equivalents:primary#1
- **Rules:** B05; B06; B07; B08; family resolve_all.NARROW[cash_and_equivalents]
- **Evidence:** 103 companies, 1156 served, 22866 proven, 131 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 2 companies, e.g. DELL cash_and_equivalents 2015-01-30 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseCashAndCashEquivalents@2021; PostconfirmationCashAndCashEquivalents@2021; PreconfirmationCashAndCashEquivalents@2021

### `NetCashProvidedByUsedInOperatingActivities`
- **Meaning:** Cash Provided by (Used in) Operating Activity, Including Discontinued Operation (us-gaap, duration). Amount of cash inflow (outflow) from operating activity, including, but not limited to, discontinued operation. Operating activity includes, but is not limited to, transaction, adjustment, and change in value not defined as investing or fin...
- **Data point definition:** cfo: Net cash provided by (used in) operating activities as printed.
- **Data point:** cfo; polarity cfo:signed; role cfo:primary#1
- **Rules:** X84
- **Evidence:** 110 companies, 1154 served, 40731 proven, 136 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `SellingGeneralAndAdministrativeExpense`
- **Meaning:** Selling, General and Administrative Expense (us-gaap, duration, debit). The aggregate total costs related to selling a firm's product and services, as well as all other general and administrative expenses. Direct selling expenses (for example, credit, warranty, and advertising) are expenses that can be directly...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; sga_expense: Selling, general and administrative expense for the period.
- **Data point:** sga_expense; operating_expenses; polarity sga_expense:positive; role sga_expense:primary#1
- **Rules:** I15; I16; I17; I18; family resolve_all.NARROW[sga_expense]
- **Evidence:** 66 companies, 1140 served, 3623 proven, 96 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces RelatedPartyTransactionSellingGeneralAndAdministrativeExpensesFromTransactionsWithRelatedParty@2023

### `AssetsCurrent`
- **Meaning:** Assets, Current (us-gaap, instant, debit). Amount of asset recognized for present right to economic benefit, classified as current.
- **Data point definition:** current_assets: Total current assets as printed on a classified balance sheet. [not applicable: bank,insurer,bdc]
- **Data point:** current_assets
- **Rules:** X39; C09; B01; B04; resolver functions resolve; regions; resolve_family
- **Evidence:** 95 companies, 1118 served, 32318 proven, 137 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCurrentAssets@2020; FreshStartAdjustmentIncreaseDecreaseCurrentAssets@2021; PostconfirmationCurrentAssets@2021; PreconfirmationCurrentAssets@2021 (+3 more)

### `PaymentsForRepurchaseOfCommonStock`
- **Meaning:** Payments for Repurchase of Common Stock (us-gaap, duration, credit). The cash outflow to reacquire common stock during the period.
- **Data point definition:** share_buybacks: Cash repurchases of the company's own common stock;  excludes tax-withholding shares, excise tax, employee-plan purchases, subsidiary buybacks and swaps (founder 2026-11-04).
- **Data point:** share_buybacks; polarity share_buybacks:positive; role share_buybacks:primary#1
- **Rules:** K10; K11; K12; K13; K14; K15; K16; resolver functions resolve_cf; family resolve_all.NARROW[share_buybacks]
- **Evidence:** 106 companies, 1118 served, 29887 proven, 130 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. AXP share_buybacks 2018-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (1)

### `PropertyPlantAndEquipmentNet`
- **Meaning:** Property, Plant, and Equipment, after Accumulated Depreciation, Depletion, and Amortization (us-gaap, instant, debit). Amount, after accumulated depreciation, depletion, and amortization, of property, plant, and equipment. Includes, but is not limited to, land and land improvement; building; machinery and equipment; furniture and fixture; and work of art, h...
- **Data point definition:** ppe_net: Property, plant and equipment net of accumulated depreciation at period end (incl. finance-lease ROU only where the filer prints them together).
- **Data point:** ppe_net; role ppe_net:primary#1
- **Rules:** B22
- **Evidence:** 106 companies, 1096 served, 32159 proven, 113 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FlightEquipmentOwnedNet@2016; FreshStartAdjustmentIncreaseDecreasePropertyAndEquipmentNet@2021; PostconfirmationPropertyAndEquipmentNet@2021; PreconfirmationPropertyAndEquipmentNet@2021

### `ShareBasedCompensation`
- **Meaning:** Share-Based Payment Arrangement, Noncash Expense (us-gaap, duration, debit). Amount of noncash expense for share-based payment arrangement.
- **Data point definition:** sbc: Stock-based compensation add-back on the cash-flow statement (pre-tax).
- **Data point:** sbc; polarity sbc:positive; role sbc:primary#1
- **Rules:** X66; K24; K25; resolver functions apply_sbc_award_members; member_facts; resolve_cf
- **Evidence:** 91 companies, 1047 served, 4504 proven, 102 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CommonStockSharesOutstanding`
- **Meaning:** Common Stock, Shares, Outstanding (us-gaap, instant). Number of shares of common stock outstanding. Common stock represent the ownership interest in a corporation.
- **Data point definition:** shares_outstanding: Common shares outstanding at period end (all economic classes).
- **Data point:** shares_outstanding; role shares_outstanding:primary#1
- **Rules:** X67; X111; B23; B24; B29; resolver functions DERIVED_YIELDS_TO; comparative_fill; fill_printed_zero_and_comparative; shares
- **Evidence:** 83 companies, 992 served, 2408 proven, 80 certified cells; last verified 2026-11-15
- **Known problems:** pattern P04 round_share_count: 3 open hit(s) at 3 companies, e.g. CVS shares_outstanding 2022-12-31 (resolver) (pattern_hits.csv); pattern P05 comparative_only_year_hidden: 1 open hit(s) at 1 companies, e.g. WFC shares_outstanding 2023-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P04 (3); P05 (1)

### `AccountsPayableCurrent`
- **Meaning:** Accounts Payable, Current (us-gaap, instant, credit). Carrying value as of the balance sheet date of liabilities incurred (and for which invoices have typically been received) and payable to vendors for goods and services received that are used in an entity's business. Used to reflect the curr...
- **Data point definition:** accounts_payable: Trade accounts payable at period end. [not applicable: bank]
- **Data point:** accounts_payable; role accounts_payable:primary#1
- **Rules:** B16; B17; B18; B19; family resolve_all.NARROW[accounts_payable]
- **Evidence:** 84 companies, 985 served, 3404 proven, 134 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AccountsPayableRelatedPartiesCurrent@2023; FreshStartAdjustmentIncreaseDecreaseAccountsPayable@2021; PostconfirmationAccountsPayable@2021; PreconfirmationAccountsPayable@2021

### `CostOfGoodsAndServicesSold`
- **Meaning:** Cost of Product and Service Sold (us-gaap, duration, debit). The aggregate costs related to goods produced and sold and services rendered by an entity during the reporting period. This excludes costs incurred during the reporting period related to financial services rendered and other revenue generat...
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#2
- **Rules:** I02; I03; I04
- **Evidence:** 65 companies, 955 served, 16174 proven, 84 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AdvertisingRevenueCost@2018; AssetManagementCosts@2018; CasinoExpenses@2018; ConcessionsCosts@2018 (+62 more)

### `Liabilities`
- **Meaning:** Liabilities (us-gaap, instant, credit). Amount of liability recognized for present obligation requiring transfer or otherwise providing economic benefit to others.
- **Data point definition:** total_liabilities: Total liabilities as printed.
- **Data point:** total_liabilities
- **Rules:** C03; F02; B25; resolver functions resolve; run; apply_tl_corroboration
- **Evidence:** 83 companies, 950 served, 29466 proven, 110 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000101829-20-000013: RTX (UTX) FY2019 10-K utx-20191231.htm consolidated balance sheet prints Total Liabilities 95,390 (2018: 93,492);  the XBRL tags only the 2018 value (R4.htm show
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationLiabilities@2020; FreshStartAdjustmentIncreaseDecreaseLiabilities@2021; PostconfirmationLiabilities@2021; PreconfirmationLiabilities@2021 (+4 more)

### `OperatingIncomeLoss`
- **Meaning:** Operating Income (Loss) (us-gaap, duration, credit). The net result for the period of deducting operating expenses from operating revenues.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; operating_income: Operating income: revenue minus all operating costs (COR, opex, restructuring and impairment), before interest, other non-operating items, equity-method income and tax. [not applicable: bank] (+1 more)
- **Data point:** operating_income; operating_expenses; other_income_expense_net
- **Rules:** C13; resolver functions resolve
- **Evidence:** 80 companies, 949 served, 34797 proven, 118 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpense`
- **Meaning:** Interest Expense, Operating and Nonoperating (us-gaap, duration, debit). Amount of interest expense classified as operating and nonoperating. Includes, but is not limited to, cost of borrowing accounted for as interest expense.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** interest_expense; other_income_expense_net; operating_expenses; interest_income; polarity interest_expense:positive; role interest_expense:primary#1
- **Rules:** X115; I21; I20; I22; I23; I24; resolver functions resolve_band; family resolve_all.NARROW[interest_expense]
- **Evidence:** 88 companies, 938 served, 24594 proven, 65 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 1 companies, e.g. META interest_expense 2021-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToInterestExpenseNet@2013; CashFlowHedgeGainReclassifiedToInterestExpense@2013; CashFlowHedgeLossReclassifiedToInterestExpense@2013; InterestExpenseRelatedParty@2023

### `PaymentsToAcquirePropertyPlantAndEquipment`
- **Meaning:** Payments to Acquire Property, Plant, and Equipment (us-gaap, duration, credit). The cash outflow associated with the acquisition of long-lived, physical assets that are used in the normal conduct of business to produce goods and services and not intended for resale; includes cash outflows to pay for construction of sel...
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive; role capex:primary#1
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX; resolve_all.NARROW[capex]
- **Evidence:** 82 companies, 914 served, 17784 proven, 110 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InventoryNet`
- **Meaning:** Inventory, Net (us-gaap, instant, debit). Amount after valuation and LIFO reserves of inventory expected to be sold, or consumed within one year or operating cycle, if longer.
- **Data point definition:** inventory: Inventories at period end as printed. [not applicable: bank,lender,broker_am,insurer,equity_reit,bdc]
- **Data point:** inventory; role inventory:primary#1
- **Rules:** B15; B14; resolver functions inventory_header_sum
- **Evidence:** 80 companies, 895 served, 3308 proven, 115 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseInventories@2021; PostconfirmationInventories@2021; PreconfirmationInventories@2021

### `InterestPaidNet`
- **Meaning:** Interest Paid, Excluding Capitalized Interest, Operating Activity (us-gaap, duration, credit). Amount of cash paid for interest, excluding capitalized interest, classified as operating activity. Includes, but is not limited to, payment to settle zero-coupon bond for accreted interest of debt discount and debt instrument with insignif...
- **Data point definition:** cash_paid_for_interest: Cash paid for interest, net of amounts capitalized (InterestPaidNet).
- **Data point:** cash_paid_for_interest; polarity cash_paid_for_interest:positive; role cash_paid_for_interest:primary#1
- **Rules:** K35
- **Evidence:** 98 companies, 883 served, 1627 proven, 90 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `IncomeTaxesPaidNet`
- **Meaning:** Income Tax Paid, after Refund Received (us-gaap, duration, credit). Amount, after refund, of cash paid to foreign, federal, state, and local jurisdictions as income tax.
- **Data point definition:** cash_paid_for_income_taxes: Cash paid for income taxes, net of refunds, as printed.
- **Data point:** cash_paid_for_income_taxes; polarity cash_paid_for_income_taxes:signed; role cash_paid_for_income_taxes:primary#1
- **Rules:** K32; K34; K33
- **Evidence:** 105 companies, 866 served, 1547 proven, 93 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000040545-17-000010: GE FY2016 10-K R7.htm statement of cash flows: Cash recovered (paid) during the year for income taxes (7,469): 7,469 paid;  IncomeTaxesPaidNet is positive for ta; filer XBRL error 0000040545-16-000145: GE FY2016 10-K R7.htm (0000040545-17-000010) prints the FY2015 column: Cash recovered (paid) during the year for income taxes (2,486): 2,486 paid;  the FY2015 10 (+2 more)
- **Pattern hits:** none

### `IncreaseDecreaseInInventories`
- **Meaning:** Increase (Decrease) in Inventories (us-gaap, duration, credit). The increase (decrease) during the reporting period in the aggregate value of all inventory held by the reporting entity, associated with underlying transactions that are classified as operating activities.
- **Data point definition:** cf_inventory_change: Cash-flow change in inventories, raw XBRL sign.
- **Data point:** cf_inventory_change; polarity cf_inventory_change:raw; role cf_inventory_change:primary#1
- **Rules:** none; family resolve_cf.WC[cf_inventory_change]
- **Evidence:** 74 companies, 862 served, 2794 proven, 117 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `IntangibleAssetsNetExcludingGoodwill`
- **Meaning:** Intangible Asset, Excluding Goodwill, after Accumulated Amortization (us-gaap, instant, debit). Amount, after accumulated amortization, of finite- and indefinite-lived intangible assets and capitalized cost for software to be sold, leased, or marketed. Excludes goodwill.
- **Data point:** intangible_assets; role intangible_assets:primary#1
- **Rules:** B21
- **Evidence:** 83 companies, 848 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
