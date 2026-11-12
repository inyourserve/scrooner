# Tag cards, ranks 1-95 of TAG-PRIORITY-2026-11-11 (Tag Expert, 2026-11-11)

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
