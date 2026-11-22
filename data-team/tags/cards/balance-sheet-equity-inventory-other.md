# Card family: equity, mezzanine, inventory, splits, sector lines and other (written 2026-11-09 by the Tag Expert; first version from relays)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->
Not FSN-write data points today; balance-sheet families are held. FSN `stockholders_equity_resolved` rules: StockholdersEquity p10, PartnersCapital p11, MembersEquity p12, PartnersCapitalAttributableToParent p13, LLC members' equity p14 (bs.jsonl). All rows below: FILING-CHECKED by the named role, not re-opened by me, unless marked.

## 1. Equity and mezzanine
- **NCI-inclusive equity as the only face total**: UNH (104,513M incl. 6,066M NCI; no StockholdersEquity fact), AT&T (126,434M incl. 15,990M NCI), HAS, LMNR; FSDS 2025q4 has 120 BS presentations with that tag + MinorityInterest and no StockholdersEquity (Standardization Lead). The FSN rules do not map `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`, so these are gaps. Derivation: parent = total − MinorityInterest, and only when the face prints both (identity A = L + total equity + temporary equity; never subtract NCI from the parent tag) (Data Engineer). FE 2017-19 10-Qs file small values (36-175M) on the NCI-inclusive tag that are not the face total: never prefer it without SE_incl − SE = NCI (Verifier 2).
- `StockholdersEquity` includes preferred stock in permanent equity (JPM 21,040M of 374,598M; PSA 4,350M of 9,190M; HIW): not common equity. BDC net assets = StockholdersEquity (ARCC "Total stockholders' equity" 14,318.0M; BXSL "Total net assets"); AssetsNet on 0 of 2 faces (Sector Analyst). HOVR files in CAD: a unit gate is required.
- Partnerships: BX, KKR file parent equity on PartnersCapital and NCI on PartnersCapitalAttributableToNoncontrollingInterest (BX also custom), no StockholdersEquity/MinorityInterest.
- **Mezzanine**: the element is `TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests` (plural; an identity-fix constant misspelled it). AMRX face "Redeemable non-controlling interests" 41,293K on it. Redeemable NCI also sits on `RedeemableNoncontrollingInterestEquityCommonCarryingAmount` (MCK 10-K year-ends: 1,386M FY2015, 1,406M FY2016, 1,327M FY2017, 1,459M FY2018, 1,393M FY2019, 1,402M FY2020, 1,271M FY2021, 0 FY2022-FY2025, 943M FY2026 (0000927653-26-000069 BS l27); the earlier "1,430M" matches no year-end: withdrawn), `…FairValue` (IPG 460.8M), `…Other` (ETP 15M; off-face at NI FY2023 1,360.0M while ET uses it for a face line). TRGP's Series A preferred mezzanine (749.7M) is filed only with a class-of-stock member. KMB `RedeemableCommonAndPreferredSecuritiesOfSubsidiaries` is mezzanine (0000055785-24-000054 R4; Verifier 2026-11-09).
## 2. Inventory (quick ratio)
- `InventoryNet` alone misses face inventory at NKE, BA, GAP, AZO, XOM, RL, DDS, MKC (Verifier 2). Face totals on other tags: `InventoryFinishedGoodsNetOfReserves` (GAP "Merchandise inventory" 2,398, NKE, AZO, SYY, LULU; a component under InventoryNet at 24 others); `InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings` (BA 81,897, LMT, HII, NOC, KTOS; equal to InventoryNet at 80 of 111 pairs); `InventoryGross` (MKC and DHR "Total inventory" beside FG/WIP/RM sub-lines, where summing double counts; the single face line at CWST, RGLD, MPLX); `InventoryRealEstate` (Zillow homes 491,293K); XOM "Inventories" is an abstract over `EnergyRelatedInventory` 22,363 + `InventoryPartsAndComponentsNetOfReserves` 3,200; LNT prints three face lines with no total; utilities print "Materials and supplies" on `InventoryRawMaterialsAndSupplies` (PEG also a custom "Fuel" 329, so a tag sum misses 919).
- FIFO: KR prints FIFO 7,998 then LIFO reserve (1,291) with no total; inventory = 6,707 only net of the face reserve.
- **Not inventory**: OMC "Work in process" on `InventoryWorkInProcess` 2015-19 = client billable costs and unbilled fees, an ASC 606 contract asset; the same amounts are also tagged `ContractWithCustomerAssetGrossCurrent`, and the face line moves to it from 2020 (Data Chief, Standardization Lead, independently re-read). `MaterialsSuppliesAndOther` (CP "Materials and supplies") is not inventory by definition. 147 cohort cells (85 companies) have InventoryNet only as non-authoritative copies, so the "unmapped" reason is wrong there (DATA-INFERRED).
- Utility R pages can hold several co-registrant balance sheets in one report (PEG R5: three AssetsCurrent rows); scope face logic to the registrant block. NI prints gross AR, allowance and net AR as three rows.
## 3. Splits (StockholdersEquityNoteStockSplitConversionRatio)
- A unit-`pure` factor, not a value source (Apple EPS 5.43 / 4). NVDA's 2024 10-for-1 is filed only on DURATION (month) contexts; GOOG 20:1 is on both announcement (2022-02-01) and effective date (2022-07-15), 164 days apart; NVDA 4:1 on two instants 46 days apart, so a 45-day merge double counts. ODFL states 1.5 for a 3-for-2 (non-integer ratios exist).
## 4. Sector and other lines
- Managed care uses insurer tags (UNH, HUM, MOH: premiums, "Medical costs", "Medical costs payable"; 6 of 7). Digital assets: `CryptoAssetFairValue*` (MSTR, COIN); `CryptoAssetNoncurrent` on no face. Utilities: suffixed `RegulatoryAssetsNoncurrent/Current` (22 of 32), plain `RegulatoryAssets` on none. Exchange clearing and insurance-broker fiduciary lines are extensions (0 of 6 exchanges, 0 of 7 brokers use us-gaap; asset-manager fee lines 0 of 14). Face frequency over 1,027 filers: RetainedEarningsAccumulatedDeficit 985, ShortTermInvestments 133, MarketableSecuritiesCurrent 72.
- `GrossInvestmentIncomeOperating` population (118 companies) is 42 BDCs, 47 insurers, 12 staking/commodity ETPs and KKR, and others; gating it to BDCs removes 2,287 rows at 76 non-BDCs. `NetInvestmentIncome` is insurer face NII but BDC PRE-tax NII (ARCC 1,458M before tax; after-tax on `InvestmentIncomeOperatingAfterExpenseAndTax`). See investment-income-and-funds.md.
- `OperatingExpenses` at REITs: OHI "Total expenses" incl. interest; DOC/HCP only the property "Operating" line (two perimeters).
- `ResearchAndDevelopmentExpense` at JNJ = only the CF add-back of acquired IPR&D (1,841M FY2024); face R&D is `…ExcludingAcquiredInProcessCost`.
- CF working capital: CMI's only AR change is `IncreaseDecreaseInAccountsAndNotesReceivable` (includes notes: a perimeter); `IncreaseDecreaseInAccountsPayableAndAccruedLiabilities` is combined (262 of 358 residue companies); never fill AP change from a BS difference (WMT 1,611 vs 4,395).
- dei: `EntityNumberOfEmployees` is filed by about 6% of the top 1,000 (a no-tag case; yfinance is not a display source). `dei:Security12bTitle` carries the ADS ratio as text on every checked cover.
- Method: a value from a tag the filer stopped using (CDNS cost of revenue 2012, GLW capex 2020, LOW interest 2011, CME shares 2010) stays the newest row unless a staleness guard compares it with the latest period (Data Engineer). In the FSN store the latest filing wins per key, so this is mostly an old-mapper issue.
## 5. Also processed here
- **Removed/never elements** (Tag Expert sector run, FASB 2025/2026 schemas): `CryptoAssetNoncurrent` never existed in our data; `LoansReceivableNet` (143 companies to 2020-03-31) and `HealthCareOrganizationPremiumRevenue` (3 to 2018-03-31) are REMOVED historical elements, so keep them for old periods only; the `AllowanceForLoanAndLeaseLosses*` roll-forward elements are components, never the allowance balance.
- `InvestmentIncomeInvestmentExpense`: TOTAL fund expenses at BDCs (ARCC 1,594M incl. interest and management fees) vs investment expenses only at insurers (CINF 17M); gross − this = NetInvestmentIncome in both, with different meanings.
- Banks, net loans on the latest 10-K face: the post-CECL tag `FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss` at 33 of 44; pre-CECL 1 of 44; any of three tags 40 of 44. Provision: any of 7 us-gaap tags 33 of 44, `ProvisionForLoanLeaseAndOtherLosses` alone 21 of 44 (Sector Analyst). See bank-loans-and-allowance.md.
- `FinanceLeaseLiabilityCurrentStatementOfFinancialPositionExtensibleList` (and Noncurrent) names the balance-sheet element that holds the finance lease (MU: DebtCurrent and LTDACLO; GOOG 2025: AccruedLiabilitiesCurrent and OtherLiabilitiesNoncurrent; AMZN: AccruedLiabilitiesCurrent and a custom). A deterministic double-count guard for the debt lane (debt.md §8).
- **Tag-name absence is evidence only for undimensioned primary-statement lines**: LLY, REGN, VRTX, ALNY, BMY disclose collaboration revenue without any "Collaborat" tag (members/extensions are not in company_sec_tag). `*ExpectedDividendRate` (option valuation) sits on non-payers; never count it as a dividend signal (Data Engineer, DATA-INFERRED).
## 6. Folded in from the FSN-expert handover (2026-11-10)
- **The equity statement's opening balance can be restated while the balance sheet print is not**: MSFT 2016-06-30 equity 83,090 on the EQ statement vs 71,997 on the BS print. A vintage-policy question (FSN-expert P-6), not a tag error.
- FSN columns vs the SEC spec (FSN-GUIDE.md on docs/fsn-expert, real rows): cal `negative` = ±1 (the weight); DIM key `dimhash` with `0x00000000` = no dimension; `iprx` is 0-based; `datp` is days (ddate − actual date); `dcml` −32768 = nil; `coreg` set only for a sole LegalEntity axis; pre.stmt can be `SI` or a mislabelled `UN` (compare the playbook README §2, GATX/Revvity).
## 7. Balance-sheet lane relay 2026-11-11 (Verifier VERIFY-BS-DERIVE-2026-11-08: 31/32 then 19/19; reports BS-DERIVE-TL-CURRENT-2026-11-02, FSN-MISSING-QUARTERS-2026-11-09)
- **SUPERSEDED 2026-11-11 (doc 02 2026-11-01 item 4: instants are never derived; decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md C4): no printed total liabilities = not_presented. Kept only as a Verifier cross-check.** Total liabilities with no printed line: (a) capitalization format: split total capitalization (NEE, sector-faces.md); (b) identity route when L&E has no calc arcs: L = L&E − total equity incl. NCI − temporary equity, every term printed (Verifier-right: ORCL 2024-08-31 132,945M; HCA 2024-06-30 56,040M; PSEG 2024-09-30 37,985M; RIG 2024-09-30 9,282M); NCI stays OUT of liabilities (DTE 2016: 22,542M).
- **Mezzanine**: a Redeemable*/Temporary* line printed after the last liability and before the first equity line is temporary equity (KMB custom `RedeemableCommonAndPreferredSecuritiesOfSubsidiaries` 26M, 0000055785-24-000054: 15,908M as a liability vs face 15,882M); a "mandatorily redeemable" (ASC 480) label stays a liability.
- `CommitmentsAndContingencies` is a blank L&E calc child in 4,326 of 4,462 derived columns; a VALUED one must refuse the derivation.
- `DeferredTaxAssetsLiabilitiesNet` as an L&E child can carry a debit balance (4 columns): never add as a liability.
- **Balance sheet under stmt UN / a second balance sheet**: PLNT pre-IPO 10-Q 0001193125-15-310710 has the shell's BS (report 2, BS) and Pla-Fit Holdings' classified BS (report 4, UN, LegalEntityAxis): "unclassified" must look at every statement of the accession (entity-and-predecessor.md).
- **Segment-split faces** (NVR, Lennar, Berkshire, Ares): pick the face column by the closing total (L&E, else Assets) being valued, not by "most lines valued".
- **Combined filings print blank lines per column** (Sempra combined 10-K 0000086521-17-000017: five current lines blank in the Sempra column; children still tie to 28,571M, Verifier-right; News Corp 2019-03-31 temporary equity blank, 5,600M right).
- **One failing subtotal blanks a whole column**: AT&T FY2019 10-K 0001562762-20-000064, 2017 column: NonoperatingIncomeExpense children −4,831M vs −4,575M printed (a child missing from the filer's calc: a filer calc gap, not a value error); PG&E FY2018 10-K 0001004980-19-000004, 2016 column: NIACSB 1,393M vs 1,407M.
## 8. FSN-expert relay part 2 (2026-11-11; top-100 faces since 2015, DATA-INFERRED with accessions; no R page opened by them)
- **Era switches (same line, new tag)**: CF deferred taxes `DeferredIncomeTaxExpenseBenefit` → `DeferredIncomeTaxesAndTaxCredits` (MSFT at Q3 FY2026 0001193125-26-191507; 23 names use the second); CF SBC `AllocatedShareBasedCompensationExpense` → `ShareBasedCompensation` (MSFT at the FY2017 10-K; 94 vs 10 names; BKNG prints SBC as an IS line); `AvailableForSaleSecuritiesCurrent` → `ShortTermInvestments` at ASU 2016-01 (MSFT Q1 FY2019); `DeferredRevenueCurrent/Noncurrent` → `ContractWithCustomerLiabilityCurrent/Noncurrent` at ASC 606 (28 → 10 vs 0 → 32 cos; TMO and INTC transition filings print both); deferred-tax BS tags at ASU 2015-17 (`DeferredTaxAssetsNetCurrent` last fy2017; `DeferredTaxLiabilitiesNoncurrent` 40 → 0 cos, `DeferredIncomeTaxLiabilitiesNet` 6 → 49); `TreasuryStockValue` 54 → 27 vs `TreasuryStockCommonValue` 4 → 36 (same label).
- `CashCashEquivalentsAndShortTermInvestments` (MSFT "Total cash, cash equivalents, and short-term investments") is a subtotal, never cash.
- **Intangibles**: `FiniteLivedIntangibleAssetsNet` is the face total "Intangible assets, net" at 18 names (MSFT ORCL CRWD LRCX MU IBM VZ TMUS DE TXN BAC ACN ANET); PEP prints finite + `IndefiniteLivedIntangibleAssetsExcludingGoodwill` with no total; **`IntangibleAssetsNetIncludingGoodwill` INCLUDES goodwill** (CB/ACE "Goodwill and other intangible assets", TJX "Goodwill and tradename", LRCX, ANET 2024+) (my SCCO "no goodwill line" claim is WITHDRAWN: SCCO files Goodwill 41.9M separately, 0001104659-26-021492): never read goodwill or intangibles from it by name. CRWD 10-Q 0001535527-20-000019 labels a BS FiniteLivedIntangibleAssetsNet line "Total amortization expense".
- **PP&E**: `PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAsset…After…` is "Property and equipment, net" at 28 names from 2019 (GOOGL, CVX): includes finance-lease ROU; the same face line within a company (AMZN 2019 72,705M under both tags, 0001018724-20-000004 / -21-000004 R6), so map ppe_net with flag `incl_finance_lease_rou`; flagged when compared across companies (111 names use PPENet).
- **Receivables**: face AR siblings `ReceivablesNetCurrent` (18; LMT, VLO; cal parent of AR net, includes non-trade), `AccountsNotesAndLoansReceivableNetCurrent` (CVX, PEP), `AccountsAndOtherReceivablesNetCurrent` (ABBV, LLY "Accounts receivable, net"), `AccountsReceivableNet` (unclassified: AXP "Card Member receivables", PLD); VZ 2020-22 prints `AccountsReceivableGrossCurrent` beside net.
- **Payables**: `AccountsPayableTradeCurrent` is THE AP line at ABT, DHR ("Trade accounts payable"); `AccountsPayableCurrentAndNoncurrent` at AXP, NEE (unclassified). META trap: FY2019 10-K 0001326801-20-000013 R2 "Accounts payable" 1,363M = AccountsPayableCurrent and "Partners payable" 886M = AccountsPayableTradeCurrent; a 2020 10-Q puts "Partners payable" on `AccountsPayableAndOtherAccruedLiabilitiesCurrent`; from 2021 META's "Accounts payable" itself is AccountsPayableTradeCurrent. So AP-trade is neither always AP nor always a component, and an "AP and accrued" tag is not always combined: pick by label + calc tree. Combined-line users of `AccountsPayableAndOtherAccruedLiabilitiesCurrent`: CRM, GE/GEV, GILD.
- **Leases**: `OperatingLeaseLiabilityNoncurrent` at 41 names but the current part only at 21 (usually inside other current liabilities: MSFT, TXT); `OperatingLeaseLiability` (total) is the face line at PLD, GE.
- **Current-line calc relations flip by filer**: AccruedLiabilitiesCurrent ← EmployeeRelated (409 arcs) / ← OtherAccrued (500); PrepaidExpenseAndOtherAssetsCurrent ← OtherAssetsCurrent (148) / ← PrepaidExpenseCurrent (76), but OtherAssetsCurrent ← PrepaidExpenseAndOther… at 38 filers: use the filing's calc tree, never a fixed hierarchy.
- **Equity parts**: `AdditionalPaidInCapitalCommonStock` (60) vs `AdditionalPaidInCapital` (44) vs combined `CommonStocksIncludingAdditionalPaidInCapital` (26; MSFT, IBM).

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.

## 9. Instants are never summed (Dhairya 2026-11-12, doc 02)
- Inventory printed only as components (SO, XOM) and shares printed only per class: not_presented. Total liabilities with no printed line: not_presented. The only summed instant is total_debt (founder definition).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 41 elements named in this card have library knowledge; the 30 most served are below. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `Goodwill`
- **Meaning:** Goodwill (us-gaap, instant, debit). Amount, after accumulated impairment loss, of asset representing future economic benefit arising from other asset acquired in business combination or from joint venture formation or both, that is not individually identified and separately r...
- **Data point definition:** goodwill: Goodwill at period end as printed.
- **Data point:** goodwill; role goodwill:primary#1
- **Rules:** X78; B20
- **Evidence:** 105 companies, 1206 served, 4387 proven, 126 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces BusinessCombinationGoodwillRecognizedSegmentAllocation@2013; FreshStartAdjustmentIncreaseDecreaseGoodwill@2021; FreshStartAdjustmentIncreaseDecreaseReorganizationValueInExcessOfAmountsAllocableToIdentifiableAssets@2021; PostconfirmationGoodwill@2021 (+2 more)

### `StockholdersEquity`
- **Meaning:** Equity, Attributable to Parent (us-gaap, instant, credit). Amount of equity (deficit) attributable to parent. Excludes temporary equity and equity attributable to noncontrolling interest.
- **Data point definition:** stockholders_equity: Equity attributable to the parent at period end.
- **Data point:** stockholders_equity
- **Rules:** X78; C06; resolver functions resolve
- **Evidence:** 104 companies, 1190 served, 22897 proven, 115 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CommonStockholdersEquity@2013; EquityMethodInvestmentSummarizedFinancialInformationEquityOrCapital@2020; FreshStartAdjustmentIncreaseDecreaseStockholdersEquity@2021; PostconfirmationStockholdersEquity@2021 (+1 more)

### `AssetsCurrent`
- **Meaning:** Assets, Current (us-gaap, instant, debit). Amount of asset recognized for present right to economic benefit, classified as current.
- **Data point definition:** current_assets: Total current assets as printed on a classified balance sheet. [not applicable: bank,insurer,bdc]
- **Data point:** current_assets
- **Rules:** X39; C09; B01; B04; resolver functions resolve; regions; resolve_family
- **Evidence:** 95 companies, 1118 served, 32318 proven, 126 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCurrentAssets@2020; FreshStartAdjustmentIncreaseDecreaseCurrentAssets@2021; PostconfirmationCurrentAssets@2021; PreconfirmationCurrentAssets@2021 (+3 more)

### `ShareBasedCompensation`
- **Meaning:** Share-Based Payment Arrangement, Noncash Expense (us-gaap, duration, debit). Amount of noncash expense for share-based payment arrangement.
- **Data point definition:** sbc: Stock-based compensation add-back on the cash-flow statement (pre-tax).
- **Data point:** sbc; polarity sbc:positive; role sbc:primary#1
- **Rules:** X66; K24; K25; resolver functions apply_sbc_award_members; member_facts; resolve_cf
- **Evidence:** 91 companies, 1047 served, 4504 proven, 91 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `AccountsPayableCurrent`
- **Meaning:** Accounts Payable, Current (us-gaap, instant, credit). Carrying value as of the balance sheet date of liabilities incurred (and for which invoices have typically been received) and payable to vendors for goods and services received that are used in an entity's business. Used to reflect the curr...
- **Data point definition:** accounts_payable: Trade accounts payable at period end. [not applicable: bank]
- **Data point:** accounts_payable; role accounts_payable:primary#1
- **Rules:** B16; B17; B18; B19; family resolve_all.NARROW[accounts_payable]
- **Evidence:** 84 companies, 985 served, 3404 proven, 123 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AccountsPayableRelatedPartiesCurrent@2023; FreshStartAdjustmentIncreaseDecreaseAccountsPayable@2021; PostconfirmationAccountsPayable@2021; PreconfirmationAccountsPayable@2021

### `ResearchAndDevelopmentExpense`
- **Meaning:** Research and Development Expense (us-gaap, duration, debit). Amount of expense for research and development. Includes, but is not limited to, cost for computer software product to be sold, leased, or otherwise marketed and writeoff of research and development assets acquired in transaction other than...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; research_and_development: Research and development expense for the period (incl. acquired IPR&D only when the filer prints it inside the R&D line). [not applicable: bank,broker_am,insurer,equity_reit,utility,bdc]
- **Data point:** research_and_development; operating_expenses; polarity research_and_development:positive; role research_and_development:primary#1
- **Rules:** I19
- **Evidence:** 66 companies, 985 served, 2774 proven, 87 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InventoryNet`
- **Meaning:** Inventory, Net (us-gaap, instant, debit). Amount after valuation and LIFO reserves of inventory expected to be sold, or consumed within one year or operating cycle, if longer.
- **Data point definition:** inventory: Inventories at period end as printed. [not applicable: bank,lender,broker_am,insurer,equity_reit,bdc]
- **Data point:** inventory; role inventory:primary#1
- **Rules:** B15; B14; resolver functions inventory_header_sum
- **Evidence:** 80 companies, 895 served, 3308 proven, 104 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseInventories@2021; PostconfirmationInventories@2021; PreconfirmationInventories@2021

### `DebtCurrent`
- **Meaning:** Debt, Current (us-gaap, instant, credit). Amount of debt and lease obligation, classified as current.
- **Data point definition:** total_debt: Total debt: short- and long-term borrowings incl. current portion, commercial paper, finance and capital leases (face or notes), financing obligations and failed sale-leasebacks;  excludes operating leases and accrued interest.
- **Data point:** total_debt
- **Rules:** none
- **Evidence:** 39 companies, 353 served, 4 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `OperatingExpenses`
- **Meaning:** Operating Expenses (us-gaap, duration, debit). Generally recurring costs associated with normal operations except for the portion of these expenses which can be clearly related to production and included in cost of sales or services. Includes selling, general and administrative expense.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#1
- **Rules:** I14; I09; I10; I11; I12; I13; family resolve_all.NARROW[operating_expenses]
- **Evidence:** 36 companies, 352 served, 11930 proven, 23 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `IncreaseDecreaseInAccountsPayableAndAccruedLiabilities`
- **Meaning:** Increase (Decrease) in Accounts Payable and Accrued Liabilities (us-gaap, duration, debit). The increase (decrease) during the reporting period in the amounts payable to vendors for goods and services received and the amount of obligations and expenses incurred but not paid.
- **Data point definition:** cf_ap_change: Cash-flow change in accounts payable, raw XBRL sign.
- **Data point:** cf_ap_change; polarity cf_ap_change:raw; role cf_ap_change:combined#1
- **Rules:** none; family resolve_cf.WC[cf_ap_change]
- **Evidence:** 34 companies, 348 served, 1 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `AllocatedShareBasedCompensationExpense`
- **Meaning:** Share-Based Payment Arrangement, Expense (us-gaap, duration, debit). Amount of expense for award under share-based payment arrangement. Excludes amount capitalized.
- **Data point definition:** sbc: Stock-based compensation add-back on the cash-flow statement (pre-tax).
- **Data point:** sbc; polarity sbc:positive; role sbc:primary#2
- **Rules:** X66; K24; K25; resolver functions apply_sbc_award_members; member_facts
- **Evidence:** 24 companies, 250 served, 183 proven, 23 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces ShareBasedCompensationArrangementByShareBasedPaymentAwardCompensationCost@2012

### `FiniteLivedIntangibleAssetsNet`
- **Meaning:** Intangible Asset, Finite-Lived, after Accumulated Amortization (us-gaap, instant, debit). Amount, after accumulated amortization, of finite-lived intangible asset. Excludes goodwill and capitalized cost for software to be sold, leased, or marketed.
- **Data point:** intangible_assets; role intangible_assets:primary#2
- **Rules:** B21
- **Evidence:** 33 companies, 245 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FiniteLivedIntangibleAssetsFutureAmortizationExpense@2012; FreshStartAdjustmentIncreaseDecreaseAmortizableIntangibleAssets@2021; PostconfirmationAmortizableIntangibleAssets@2021; PreconfirmationAmortizableIntangibleAssetsNet@2021

### `OtherLiabilitiesNoncurrent`
- **Meaning:** Other Liabilities, Noncurrent (us-gaap, instant, credit). Amount of liabilities classified as other, due after one year or the normal operating cycle, if longer.
- **Data point definition:** total_liabilities: Total liabilities as printed.
- **Data point:** total_liabilities
- **Rules:** none
- **Evidence:** 23 companies, 198 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DueToAffiliateNoncurrent@2023; DueToEmployeesNoncurrent@2023; DueToOfficersOrStockholdersNoncurrent@2023; DueToOtherRelatedPartiesNoncurrent@2023 (+5 more)

### `NonoperatingIncomeExpense`
- **Meaning:** Nonoperating Income (Expense) (us-gaap, duration, credit). The aggregate amount of income or expense from ancillary business-related activities (that is to say, excluding major activities considered part of the normal operations of the business).
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** other_income_expense_net; interest_income; interest_expense; operating_expenses; polarity other_income_expense_net:signed; role other_income_expense_net:primary#1
- **Rules:** I29; I28; I30; I31; I32; I33; I34; I35; resolver functions resolve_band
- **Evidence:** 28 companies, 183 served, 242 proven, 14 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `ReceivablesNetCurrent`
- **Meaning:** Receivables, Net, Current (us-gaap, instant, debit). The total amount due to the entity within one year of the balance sheet date (or one operating cycle, if longer) from outside sources, including trade accounts receivable, notes and loans receivable, as well as any other types of receivable...
- **Data point definition:** accounts_receivable: Trade accounts receivable, net of allowance, at period end. [not applicable: bank]
- **Data point:** accounts_receivable; role accounts_receivable:primary#2
- **Rules:** B09; B10; B11; B12; B13; B30
- **Evidence:** 16 companies, 133 served, 498 proven, 23 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseReceivablesNet@2021; PostconfirmationReceivablesNet@2021; PreconfirmationReceivablesNet@2021

### `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`
- **Meaning:** Equity, Including Portion Attributable to Noncontrolling Interest (us-gaap, instant, credit). Amount of equity (deficit) attributable to parent and noncontrolling interest. Excludes temporary equity.
- **Data point definition:** stockholders_equity: Equity attributable to the parent at period end.; total_liabilities: Total liabilities as printed.
- **Data point:** stockholders_equity; total_liabilities
- **Rules:** none
- **Evidence:** 16 companies, 115 served, 2197 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfNewAccountingPrincipleInPeriodOfAdoption@2020; EquityMethodInvestmentSummarizedFinancialInformationEquity@2020; ImpactOfRestatementOnOpeningRetainedEarningsNetOfTax@2020; StockholdersEquityIncludingPortionAttributableToNoncontrollingInterestAdjustedBalance1@2020

### `AccountsPayableTradeCurrent`
- **Meaning:** Accounts Payable, Trade, Current (us-gaap, instant, credit). Carrying value as of the balance sheet date of obligations incurred (and for which invoices have typically been received) and payable to vendors for goods and services received that are used in an entity's business. Used to reflect the curr...
- **Data point definition:** accounts_payable: Trade accounts payable at period end. [not applicable: bank]
- **Data point:** accounts_payable; role accounts_payable:primary#2
- **Rules:** B16; B17; B18; B19; family resolve_all.NARROW[accounts_payable]
- **Evidence:** 12 companies, 112 served, 301 proven, 1 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `DeferredIncomeTaxLiabilitiesNet`
- **Meaning:** Deferred Income Tax Liabilities, Net (us-gaap, instant, credit). Amount, after deferred tax asset, of deferred tax liability attributable to taxable differences with jurisdictional netting.
- **Data point definition:** total_liabilities: Total liabilities as printed.
- **Data point:** total_liabilities
- **Rules:** none
- **Evidence:** 12 companies, 78 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseDeferredIncomeTaxLiabilitiesCurrent@2021; FreshStartAdjustmentIncreaseDecreaseDeferredIncomeTaxLiabilitiesNoncurrent@2021; PostconfirmationDeferredIncomeTaxLiabilitiesCurrent@2021; PostconfirmationDeferredIncomeTaxLiabilitiesNoncurrent@2021 (+2 more)

### `DeferredTaxLiabilitiesNoncurrent`
- **Meaning:** Deferred Tax Liabilities, Net, Noncurrent (Deprecated 2022) (us-gaap, instant, credit). Amount, after deferred tax asset, of deferred tax liability attributable to taxable differences, with jurisdictional netting and classified as noncurrent.
- **Data point definition:** total_liabilities: Total liabilities as printed.
- **Data point:** total_liabilities
- **Rules:** none
- **Evidence:** 15 companies, 61 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none

### `ProvisionForLoanLeaseAndOtherLosses`
- **Meaning:** Provision for Loan, Lease, and Other Losses (us-gaap, duration, debit). Amount of expense related loan transactions, lease transactions, credit loss from transactions other than loan and lease transactions, and other loss based on assessment of uncollectability from the counterparty to reduce the account to the...
- **Data point definition:** provision_for_credit_losses: Provision for credit losses (loan losses pre-CECL) as printed;  a release is a real negative. [not applicable: general,insurer,equity_reit,utility,bdc]
- **Data point:** provision_for_credit_losses; polarity provision_for_credit_losses:signed; role provision_for_credit_losses:primary#1
- **Rules:** none
- **Evidence:** 8 companies, 58 served, 287 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FinancingReceivableAllowanceForCreditLossesProvisions@2012

### `IncreaseDecreaseInAccountsAndNotesReceivable`
- **Meaning:** Increase (Decrease) in Accounts and Notes Receivable (us-gaap, duration, credit). The increase (decrease) during the reporting period of the sum of amounts due within one year (or one business cycle) from customers for the credit sale of goods and services; and from note holders for outstanding loans.
- **Data point definition:** cf_ar_change: Cash-flow change in accounts receivable, raw XBRL sign.
- **Data point:** cf_ar_change; polarity cf_ar_change:raw; role cf_ar_change:primary#4
- **Rules:** K30; family resolve_cf.WC[cf_ar_change]
- **Evidence:** 5 companies, 50 served, 103 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `MinorityInterest`
- **Meaning:** Equity, Attributable to Noncontrolling Interest (us-gaap, instant, credit). Amount of equity (deficit) attributable to noncontrolling interest. Excludes temporary equity.
- **Data point definition:** stockholders_equity: Equity attributable to the parent at period end.
- **Data point:** stockholders_equity
- **Rules:** none
- **Evidence:** 4 companies, 47 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationMinorityInterest@2020; NoncontrollingInterestBalanceSheetLocation@2016

### `AccountsNotesAndLoansReceivableNetCurrent`
- **Meaning:** Accounts and Financing Receivable, after Allowance for Credit Loss, Current (us-gaap, instant, debit). Amount, after allowance for credit loss, of accounts and financing receivables, classified as current. Includes, but is not limited to, notes and loan receivable.
- **Data point definition:** accounts_receivable: Trade accounts receivable, net of allowance, at period end. [not applicable: bank]
- **Data point:** accounts_receivable; role accounts_receivable:primary#3
- **Rules:** B09; B10; B11; B12; B13; B30
- **Evidence:** 5 companies, 43 served, 159 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `OperatingLeaseLiabilityNoncurrent`
- **Meaning:** Operating Lease, Liability, Noncurrent (us-gaap, instant, credit). Present value of lessee's discounted obligation for lease payments from operating lease, classified as noncurrent.
- **Data point definition:** total_liabilities: Total liabilities as printed.
- **Data point:** total_liabilities
- **Rules:** none
- **Evidence:** 6 companies, 34 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none

### `AccountsReceivableNet`
- **Meaning:** Accounts Receivable, after Allowance for Credit Loss (us-gaap, instant, debit). Amount, after allowance for credit loss, of right to consideration from customer for product sold and service rendered in normal course of business.
- **Data point definition:** accounts_receivable: Trade accounts receivable, net of allowance, at period end. [not applicable: bank]
- **Data point:** accounts_receivable; role accounts_receivable:primary#4
- **Rules:** X100; B09; B10; B11; B12; B13; B30
- **Evidence:** 3 companies, 31 served, 141 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AccountsReceivableRelatedParties@2023

### `AccountsAndOtherReceivablesNetCurrent`
- **Meaning:** Accounts and Other Receivables, Net, Current (us-gaap, instant, debit). Amount, after allowance, receivable from customers, clients, or other third-parties, and receivables classified as other due within one year or the normal operating cycle, if longer.
- **Data point definition:** accounts_receivable: Trade accounts receivable, net of allowance, at period end. [not applicable: bank]
- **Data point:** accounts_receivable; role accounts_receivable:primary#5
- **Rules:** B09; B10; B11; B12; B13; B30
- **Evidence:** 4 companies, 31 served, 95 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `AccountsPayableCurrentAndNoncurrent`
- **Meaning:** Accounts Payable (us-gaap, instant, credit). Carrying value as of the balance sheet date of liabilities incurred (and for which invoices have typically been received) and payable to vendors for goods and services received that are used in an entity's business.
- **Data point definition:** accounts_payable: Trade accounts payable at period end. [not applicable: bank]
- **Data point:** accounts_payable; role accounts_payable:primary#3
- **Rules:** B16; B17; B18; B19
- **Evidence:** 3 companies, 30 served, 98 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AccountsPayableRelatedPartiesCurrentAndNoncurrent@2023

### `InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings`
- **Meaning:** Inventory, Net of Allowances, Customer Advances and Progress Billings (us-gaap, instant, debit). Amount, after deduction of valuation reserves, other allowances, and customer advances received on long-term contracts or programs, of inventory expected to be converted to cash, sold or exchanged within the normal operating cycle.
- **Data point definition:** inventory: Inventories at period end as printed. [not applicable: bank,lender,broker_am,insurer,equity_reit,bdc]
- **Data point:** inventory; role inventory:primary#5
- **Rules:** B14; B15
- **Evidence:** 2 companies, 23 served, 87 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss`
- **Meaning:** Financing Receivable, Excluding Accrued Interest, after Allowance for Credit Loss (us-gaap, instant, debit). Amortized cost excluding accrued interest, after allowance for credit loss, of financing receivable. Excludes net investment in lease.
- **Data point definition:** loans_net: Loans net of the allowance for credit losses at period end. [not applicable: general,insurer,equity_reit,utility,bdc]
- **Data point:** loans_net; role loans_net:primary#2
- **Rules:** B28
- **Evidence:** 5 companies, 21 served, 89 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `MaterialsSuppliesAndOther`
- **Meaning:** Materials, Supplies, and Other (us-gaap, instant, debit). The carrying amount of capitalized costs of materials, supplies, and other assets, which are not included in inventory but used in production.
- **Data point definition:** inventory: Inventories at period end as printed. [not applicable: bank,lender,broker_am,insurer,equity_reit,bdc]
- **Data point:** inventory; role inventory:primary#6
- **Rules:** B14; B15
- **Evidence:** 1 companies, 12 served, 47 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
