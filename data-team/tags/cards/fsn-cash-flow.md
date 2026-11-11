# Card family: Cash flow statement tags, FSN learning pass (Tag Expert, 2026-11-11)

Scope: the 28 us-gaap cash-flow tags in the top 140 by number of top-1,000 companies. Machine-readable twin: `data-team/tags/library/fsn-cash-flow.csv` (one row per tag; that file is the seed input, this card is the reasoning). Method: "FSN for learning, SEC for mapping." Extends `cash.md`, `debt.md`, `interest.md`. Where this card and those cards meet, they agree. No earlier claim is contradicted.

## 0. Method, sources and limits

- **Official meaning.** FASB us-gaap 2026 taxonomy (`us-gaap-2026.zip`, read 2026-11-11). Sources: `elts/us-gaap-doc-2026.xml` for definitions, `-lab-` for labels, `stm/us-gaap-stm-scf-*-cal-2026.xml` for calc parents and weights. Period type and balance come from `pipeline/scripts/slot_records/results/us_gaap_2025_elements.csv`. All 28 tags are duration, monetary and non-abstract. None is deprecated in 2026.
- **FSN usage.**
  - All `fsn.line` rows for the 28 tags with `fsn.filing.period >= 2015-01-01`: 475,000+ lines, 1,001 companies. Plus `fsn.calc_arc` for each company's latest 10-K (999 filings, period 2023 or later) and an FY2015-2017 10-K (838 filings).
  - Labels were normalised to lower case. Counts are distinct companies.
  - Sector comes from `core.company.sic_code`: bank 6021/6022, insurer 63xx, REIT 6798, utility 49xx.
  - The FSN store covers only about 517 companies in 2015-2016, rising to about 990 by 2025. Year counts before 2018 reflect what the store holds, not real usage.
- **Current mapping.** `fsn.line_map` (2026-11-11 read) maps only five of these tags:
  - NetCashProvidedByUsedInOperatingActivities -> `cfo_resolved`
  - PaymentsForRepurchaseOfCommonStock -> `share_buybacks_resolved`
  - PaymentsToAcquirePropertyPlantAndEquipment -> `capex_resolved` (17,663 mapped, 4,747 unmapped)
  - DepreciationDepletionAndAmortization -> `depreciation_and_amortization_resolved` (11,871 mapped, 405 combined)
  - PaymentsOfDividendsCommonStock -> `dividends_paid_resolved`
  - Everything else is `unmapped`, or has no `line_map` row (about 270 companies not processed yet).
- **Filings opened on sec.gov.** R pages were fetched with the declared User-Agent, at most 1 request per second: AAPL, JPM, PGR, DUK (R8 plus co-registrant R14), O, XOM, ETSY (FY2017), FIVE (Q2 2020), SLB, TEVA, HPQ, SNOW, AFL, CRM, BXP, HCA, EOG, PODD, MAR, TRMB, CCL, EWBC (FY2021) and LRCX.
- **Signs.** Stored signs were checked on `data.sec.gov` companyconcept for AAPL, PODD and TRMB.
- **Concept keys.** Only keys that exist in `analytics.canonical_concept` (statement = cash_flow, plus `sbc` and the D&A key) are used. For a tag with no catalogue concept, the decision is `excluded` with that reason: it is a component of a mapped total, kept for proof, not served.
- **Scratch files.** `/private/tmp/claude-501/-Users-vikash-scrooner/65fdba90-5f59-4bea-890d-a333f876958e/scratchpad/{cf,rp,api,tools}`.

## 1. Rules that hold for every tag here (FILING-CHECKED)

1. **Sign: the stored value follows the element's own direction.** The printed sign is the stored value times -1 where `fsn.line.negating = t`.
   - Payments* and IncreaseDecreaseIn(asset) tags: positive means a cash outflow, and they print in parentheses. Examples: AAPL capex (12,715) is stored +12,715,000,000; AAPL other investing (1,480) is stored +1,480,000,000.
   - OtherNoncashIncomeExpense and GainsLossesOnExtinguishmentOfDebt are stored as income or gain.
     - AAPL prints "Other" (89) and stores +89,000,000.
     - PODD prints "Loss on extinguishment of debt" 123.9 and stores -123,900,000.
   - A "Proceeds" tag can be negative: TRMB "Issuance of common stock, net of tax withholdings" is (32.5), stored -32,500,000.
   - The SEC-API mapper must carry a per-tag sign rule (CSV column `sign_rule`). It must never use abs().
2. **Statement `UN` = co-registrant (subsidiary) cash-flow statements.** About 45 companies, mostly utilities, plus AAL, ELV, HST, CUBE and others.
   - These statements use the same tags with the subsidiary's values. Example: DUK 0001326160-26-000014 R14, Duke Energy Carolinas, CFO 3,621M against Duke consolidated 12,330M in R8.
   - In FSN, exclude every `UN` row. In companyfacts, the subsidiary values sit under the subsidiary's own CIK. Still check `dei:LegalEntityAxis` before trusting a parent-CIK fact.
3. **Totals use the plain tags (including discontinued operations, by definition).** The filer's own label may still say "continuing".
   - HPQ R6 and AAPL R8 put the plain total under a "...ContinuingOperationsAbstract" header.
   - About 35-54 companies print a separate continuing-operations total (AMD, C, DRI, MRK, NPO, ICE, IR).
   - The basis is chosen per series, not per period (inbox 2026-10-22, AMD case).
4. **ASU 2016-18 era break (cash roll-forward tags).**
   - Calc parent of the three section totals: in FY2015-17 10-Ks, `CashAndCashEquivalentsPeriodIncreaseDecrease` in 517 of 607 companies. In the latest 10-Ks, the restricted-inclusive `...PeriodIncreaseDecreaseIncludingExchangeRateEffect` in 883 of 973, and `...ExcludingExchangeRateEffect` in 82.
   - The restricted-inclusive change tag appears in FSN from 2017 (71 companies), 372 in 2018 and 676 in 2019. ETSY FY2017 (0001370637-18-000020 R7) still uses the old tags.
5. **Label checks are needed on the five mapped tags.** The tag is right far more often than the label suggests; for example, EWBC prints just "Purchases" under a "Premises and equipment:" header (0001069157-22-000031 R9). But labels reveal perimeter breaks in a minority of companies, counted per tag below. A perimeter break is `combined`, not `map` (doc 02 line 134).

## 2. Per-tag sections

Companies = distinct top-1,000 companies with a CF-statement line, FY2015+. Sign notes: section 1. Evidence class: FILING-CHECKED where a filing is cited; counts are DATA-INFERRED from FSN.

### NetCashProvidedByUsedInOperatingActivities (998 companies)

- **Meaning.** "Cash Provided by (Used in) Operating Activity, Including Discontinued Operation". No balance attribute. FASB calc: child of the cash-change total; children are ProfitLoss + Adjustments + discontinued-ops CFO.
- **Labels.** 236 variants: "net cash provided by operating activities" (772), "... (used in) ..." (457), "net cash used in ..." (248). Odd labels come from single-filing tagging errors: BSX 2016 and ASTS 2020 tag an investing total with it; MANH misspells it.
- **Decision.** Map to `cfo_resolved`. JPM FY2025 CFO is -147,782M, driven by trading assets: it is valid, but FCF stays OUT for banks and insurers.
- **Evidence.** AAPL 111,482M; JPM -147,782M; PGR 17,548M; DUK 12,330M.

### NetCashProvidedByUsedInInvestingActivities (999 companies)

- **Meaning.** Including discontinued operations; debit balance; same tree as CFO.
- **Labels.** 263 variants, all investing totals apart from typo or one-off errors (ORI "total", IONS "nvesting").
- **Decision.** Map to `cash_flow_investing_resolved`, with the same UN and basis rules as CFO.
- **Evidence.** AAPL 15,195M; JPM -265,565M; O -5,663,173K.

### NetCashProvidedByUsedInFinancingActivities (1,001 companies)

- **Meaning and use.** As for investing.
- **Decision.** Map to `cash_flow_financing_resolved`.
- **Evidence.** AAPL -120,686M; PGR -3,037M; DUK 1,950M.

### CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect (943 companies)

- **Meaning.** Change in cash plus restricted cash, including FX and discontinued operations. FASB children: the excluding-FX change plus the FX effect.
- **Labels.** 594 variants. Many still say "cash and cash equivalents" after 2018 (275 "net increase (decrease) in cash and cash equivalents").
- **Odd case (FILING-CHECKED).** SLB 0000950170-23-014656 R6 tags "Net decrease in cash before translation effect" (155)M with this INCLUDING-FX tag. The translation effect, 1M, is on the next line, on the IncludingDisposalGroup FX tag, so the real change is (154)M.
- **Decision.** Excluded: no concept (cash roll-forward). Era from 2017. The pre-2018 equivalent is `CashAndCashEquivalentsPeriodIncreaseDecrease`.

### EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents (594 companies)

- **Meaning.** FX effect, continuing operations. Its parent is the IncludingDisposalGroup variant, which SLB and HPQ use instead.
- **Labels.** 231 variants. TEVA and PAA say "translation adjustment"; RJF puts cash segregated pursuant to regulation in the perimeter.
- **Bank perimeter.** JPM R9: "Effect of exchange rate changes on cash and due from banks and deposits with banks" 17,835M.
- **Decision.** Excluded (no concept). Era from 2017; ETSY FY2017 uses EffectOfExchangeRateOnCashAndCashEquivalents.

### PaymentsForRepurchaseOfCommonStock (884 companies) -- MAPPED, label check required

- **Meaning.** "The cash outflow to reacquire common stock". FASB parent: PaymentsForRepurchaseOfEquity.
- **Usage.** Filer calc parent is the financing total, weight -1 (718 of 738 late 10-Ks). Negating in 27,420 of 27,708 lines. 27 companies also use it on the equity statement; ignore those rows.
- **Labels.** 588 variants: "repurchase(s) of common stock" (418), "purchase(s) of treasury stock" (133).
- **Perimeter breaks under doc 02 2026-11-04 item 4 (buybacks exclude excise tax and tax-withholding shares):**
  - **Excise tax included, 33 companies.** LRCX 0000707549-25-000014 R6 line 17: "Treasury stock purchases, including excise tax payments" (1,694,723)K, FILING-CHECKED. Also MRNA, MUR, DRI, FICO, ZTS, HLT, TOL, POOL and others. -> combined (no split on the face).
  - **Tax-withholding wording, 55 companies.**
    - FIVE labels this tag "Common shares withheld for taxes" in 18 filings, 2016-04 to 2020-10. From Q1 2020, a second row with the same label sits on PaymentsRelatedToTaxWithholding: 0001177609-20-000030 R6, (12,663)K against (3,789)K. That points to a label error for 2020 but leaves FY2016-2019 open: label FILING-CHECKED, amount split not verified, needs the HTML.
    - ETSY FY2017 0001370637-18-000020 R7: two rows both labelled "Repurchase of stock for tax on RSU vesting", (10,301)K on this tag and (6,417)K on PaymentsForRepurchaseOfEquity. In every other period, ETSY's label on this tag is "repurchase of stock" (39 filings). This is a label error; the tag is the buyback.
    - IP, MCK, RL, SAIC, FISV, RPM: "repurchases ... and shares withheld for taxes" -> combined.
    - PEGA, WTFC, REXR, BRX: "repurchases for tax withholdings" -> exclude.
  - **Other.** PGR does not use the tag: it files custom open-market and withholding tags (R7), matching the cloud decision.
- **Decision.** Map to `share_buybacks_resolved` only where the label passes. The excise and withholding wording above -> combined or exclude, per filing.

### PaymentsRelatedToTaxWithholdingForShareBasedCompensation (522 companies)

- **Meaning.** Cash to satisfy the grantee's tax withholding. FASB parent: the financing total, weight -1.
- **Evidence.** AAPL (5,960)M; SNOW (672,867)K; SLB (88)M.
- **Decision.** Excluded. It is never a buyback (doc 02 item 4; cloud IBM row agrees). 83 label groups are off-pattern ("repurchase of common shares in conjunction with equity award plans", BRX, REG): the tag is correct, the wording is not.

### ShareBasedCompensation (853 companies)

- **Meaning.** "Share-Based Payment Arrangement, Noncash Expense". Debit. FASB children: RestrictedStockExpense, StockOptionPlanExpense, ESOP expense.
- **Labels.** "stock-based compensation (expense)" dominates.
- **Odd uses.**
  - CRM puts it on the income-statement parenthetical by line item (0001108524-26-000190 R4: 906M = 147+111+301+2+345). Take the CF line.
  - 13 companies use perimeter wording -> combined: CSL and GBCI "net of tax benefit"; AJG, KKR, MTSI and EVR "and other non-cash compensation"; WMS "ESOP and ...".
  - "Net of amounts capitalized" (SNOW 1,599,547K, DDOG) is still the expense: map.
  - PGR uses the child RestrictedStockExpense instead.
- **Decision.** Map to `sbc`.

### PaymentsToAcquirePropertyPlantAndEquipment (769 companies) -- MAPPED

- **Meaning.** Outflow for long-lived physical assets, including self-constructed assets. FASB parent: PaymentsToAcquireProductiveAssets. Filer parent: the investing total, weight -1 (667 of 687).
- **Labels.** "purchases of property and equipment" (189), "capital expenditures" (185), and 489 variants.
- **Perimeter wording (96 companies) is consistent with doc 02 item 3, which includes capitalized software:**
  - "purchases of property, equipment and capitalized software" (UNH, MOH, WEX)
  - MAR "capital and technology expenditures" (0001048286-26-000035 R6)
  - XOM "additions to PP&E" (28,358)M
- **REITs.** Only 14 of 53 use the tag. O (R7) uses PaymentsToAcquireCommercialRealEstate plus PaymentsForCapitalImprovements. BXP (R9) uses AcquireCommercialRealEstate plus AcquireOtherProductiveAssets ("construction in progress"). For REITs, capex comes from those lines under the doc 02 perimeter.
- **Banks.** "Purchases" under a premises header (EWBC).
- **Decision.** Map to `capex_resolved` as one capex-class line. Total capex = this line plus the other capex-class lines the filer prints. MCD ruling: PaymentsToAcquireProductiveAssets beside it is not capex. NEE ruling: nuclear fuel included.

### PaymentsToAcquireBusinessesNetOfCashAcquired (798 companies)

- **Meaning.** Business-combination outflow net of cash acquired.
- **Labels.** 1,224 variants.
- **Perimeter.** 92 companies widen it to assets, investments or intangibles: ABBV and BAX "acquisitions and investments"; REGN, PEN and PCOR "asset acquisition"; A, AYI and KEYS "businesses and intangible assets".
- **Odd case.** BXP R9 uses it for "Acquisition of real estate upon consolidation of unconsolidated joint venture", with +6,086K (an inflow) in FY2024.
- **Decision.** Excluded (no concept; component of the investing total).
- **Evidence.** JPM First Republic (2,362)M; ETSY (7,880)K.

### PaymentsForProceedsFromOtherInvestingActivities (686 companies)

- **Meaning.** Other investing; positive is an OUTflow (FASB weight -1).
- **Labels.** "other", "other, net". 84 label groups at 51 companies are named items folded in (cost-method investments, grants, loans).
- **Decision.** Excluded.
- **Evidence.** AAPL (1,480)M stored +1,480M; JPM (12,665)M; DUK (1,079)M.

### ProceedsFromPaymentsForOtherFinancingActivities (679 companies)

- **Meaning.** Other financing; positive is an inflow.
- **Labels.** 62 groups at 45 companies are named items: contingent consideration (RSG, WST, LPLA, QXO), debt issuance costs (EFX, KEYS).
- **Decision.** Excluded.
- **Evidence.** AAPL (111)M; DUK 114M.

### InterestPaidNet (697 companies)

- **Meaning.** 2026 label "Interest Paid, Excluding Capitalized Interest, Operating Activity". No calc arcs in filer trees (supplemental disclosure). 841 lines are negating.
- **Bank perimeter.** Bank interest paid is mostly interest on deposits: JPM 96,436M. It is not comparable with corporate interest paid.
- **Decision.** Excluded (no concept).
- **Evidence.** JPM R9; DUK 3,590M; HCA 2,207M.

### IncomeTaxesPaidNet (564 companies)

- **Meaning.** Tax paid after refunds.
- **Labels.** "Net of refunds" wording (308 companies) is the definition, not a break.
- **Sign.** Negative means a net refund: DUK FY2025 (625)M "includes transferable credits".
- **Decision.** Excluded (no concept).
- **Evidence.** AAPL 43,369M; JPM 5,309M; HCA 1,740M.

### DeferredIncomeTaxExpenseBenefit (640 companies)

- **Meaning.** Deferred tax expense, continuing operations.
- **Usage.** The same tag is the deferred line of the tax note (filer parent IncomeTaxExpenseBenefit in 675 late 10-Ks) and the face IS split at insurers: AFL 0001628280-26-011402 R3 "Deferred" (228)M.
- **Siblings.** DUK, HCA and O use DeferredIncomeTaxesAndTaxCredits, which includes credits. TEVA uses a custom tag that includes uncertain tax positions.
- **Decision.** Excluded (detail of CFO; agrees with the Mac library).
- **Evidence.** JPM 5,611M; XOM 765M; SNOW (2,337)K.

### IncreaseDecreaseInAccountsReceivable (596 companies) -- concept `cf_ar_change`

- **Meaning.** Change in customer receivables due within a year. Credit balance: a positive value is an increase, which reduces cash.
- **Labels.** "accounts receivable" (360), ", net" (119).
- **Perimeter wording, 38 companies -> combined:**
  - BXP (R9) "Tenant and other receivables, net"; VNO and MAC
  - CLH and WAB unbilled
  - CTVA, NVT and PNR "accounts and notes"
  - WEC and IDA unbilled revenues
- **Misuse.** FRHC tags credit-loss provisions with it: exclude.
- **Sector.** No bank uses it; insurers 5.
- **Decision.** Map to `cf_ar_change`, with the label check.
- **Evidence.** AAPL (6,682)M; ETSY (8,826)K.

### IncreaseDecreaseInInventories (564 companies) -- concept `cf_inventory_change`

- **Meaning.** Change in all inventory. Credit balance.
- **Utilities.** 37 utilities use it for materials, supplies, fuel and gas in storage (AEE, FE, PPL, ATO, OKE, ED). That is inventory by definition: map (DATA-INFERRED; no utility filing opened for that label).
- **Combined.** "inventories and other" (RRC) and "inventories and contracts in progress" (RTX).
- **Decision.** Map to `cf_inventory_change`.
- **Evidence.** AAPL 1,400M; XOM (4,300)M; DUK (63)M; CCL 77M.

### IncreaseDecreaseInAccountsPayable (472 companies) -- concept `cf_ap_change`

- **Meaning.** Change in vendor payables.
- **Perimeter wording, 16 companies -> combined:**
  - XOM 0000034088-26-000045 R7: "Accounts and other payables increase/(reduction)" (222)M (FILING-CHECKED)
  - MATX, BAM and INSM "and accrued liabilities"
  - REG, WSO and EXEL "and other liabilities"
- **Sibling.** IncreaseDecreaseInAccountsPayableAndAccruedLiabilities is never `cf_ap_change` (INDEX row; PGR R7 and O R7 print it).
- **Decision.** Map to `cf_ap_change`, with the label check.

### IncreaseDecreaseInPrepaidDeferredExpenseAndOtherAssets (416 companies)

- **Use.** JPM R9 uses it for bank "Other assets" (12,582)M.
- **Decision.** Excluded (detail of CFO).
- **Evidence.** ETSY; FIVE; SNOW; BXP.

### DepreciationDepletionAndAmortization (584 on the CF; 145 also on the IS) -- MAPPED, label check required

- **Meaning.** "Aggregate expense ... allocates the cost of tangible, intangible or depleting assets". FASB children: Depreciation, AdjustmentForAmortization, Depletion, OtherDepreciationAndAmortization.
- **Filer parents.** CFO (469 late 10-Ks), CostsAndExpenses (77, IS use), OperatingIncomeLoss (28).
- **Perimeter wording, 32 companies (FILING-CHECKED at 3) -> combined:**
  - XOM R7: "Depreciation and depletion (includes impairments)" 25,993M
  - HPQ 0000047217-26-000051 R6: "Depreciation, amortization and impairment" 722M; AMCR, NXPI, WEX the same
  - DUK R8: "Depreciation, amortization and accretion (including amortization of nuclear fuel)" 7,704M
  - ACN, AMGN and ANET "and other"; WM and LB accretion; VNO including deferred financing costs
  - This follows the cloud ACN ("depreciation, amortization and other") and ISRG rulings.
- **IS against CF.** IS and CF values can differ (AEO; INDEX). Take the CF line.
- **Banks.** Banks use DepreciationAmortizationAndAccretionNet (JPM R9).
- **Decision.** Map where the label passes.

### OtherNoncashIncomeExpense (540 companies)

- **Meaning.** Other noncash income (expense). FASB weight -1 under adjustments, so a positive stored value is income, subtracted from CFO.
- **Usage.** Negating in 16,570 of 16,845 lines. 25 companies use it for named items: non-cash interest (ASTS, CRWD), bad debt (IBKR), Venezuela devaluation (KHC 2015).
- **Decision.** Excluded.
- **Evidence.** AAPL prints (89)M, stored +89M; JPM 1,309M.

### GainsLossesOnExtinguishmentOfDebt (493 on the CF; 336 also on the IS)

- **Meaning.** Gain (positive) or loss on extinguishment; credit balance. Filer parents: CFO with weight -1 (182), pretax income (65), NonoperatingIncomeExpense (54).
- **Sign.** PODD 0001145197-26-000169: the CF prints 123.9 (negating) and the IS prints the loss, stored -123.9M.
- **Labels.** CCL 0000815097-21-000027 R6 "Loss on repurchases of Convertible Notes" 464M is an extinguishment.
- **Decision.** Excluded (no concept).

### RepaymentsOfLongTermDebt (581 companies)

- **Meaning.** Outflow on debt with initial maturity over one year. 14 FASB children: convertible, FHLB, secured, senior and others.
- **Perimeter wording, 27 companies:**
  - Revolver: TRMB 0000864749-26-000108 R7 "Payments on debt and revolving credit lines" (729.5)M, while its draws are on ProceedsFromLongTermLinesOfCredit.
  - Commercial paper: GWW.
  - Capital leases: TAP, NYT, XPO, QSR.
- **Decision.** Excluded (no concept).
- **Evidence.** AAPL (10,932)M; DUK (5,652)M; XOM (1,108)M; MAR (755)M.

### ProceedsFromIssuanceOfLongTermDebt (590 companies)

- **Perimeter.** Revolver or CP draws at 23 companies (KEYS, GAP, AVAV, INTU). Net of issuance costs or discount is common (AAPL "term debt, net" 4,481M).
- **Decision.** Excluded.
- **Evidence.** DUK 11,891M; XOM 2,311M; MAR 1,425M.

### PaymentsOfDebtIssuanceCosts (467 companies)

- **Perimeter.** EOG 0000821189-26-000149 R7 "Debt Issuance and Other Financing Costs" (7)M; also LNG, CQP and EXE. CIEN and VIAV include equity costs.
- **Decision.** Excluded.
- **Evidence.** O (88,365)K.

### PaymentsOfDividendsCommonStock (447 companies) -- MAPPED

- **Meaning.** Ordinary dividends to the parent's common shareholders. FASB parent: PaymentsOfOrdinaryDividends.
- **REITs and MLPs.** "Distributions to common stockholders" (25 companies: O R7 (2,920,895)K, VTR, UDR, AMT) are common dividends: map.
- **Siblings.** Many payers use a sibling instead of this tag:
  - PaymentsOfDividends (AAPL R8 incl. dividend equivalents; JPM; LRCX)
  - PaymentsOfOrdinaryDividends (DUK R8; PFE)
  - The sibling decision is in INDEX and the inbox. This tag alone under-covers payers.
- **Decision.** Map to `dividends_paid_resolved`.
- **Evidence.** PGR (2,871)M; XOM (17,231)M.

### ProceedsFromSaleOfPropertyPlantAndEquipment (459 companies)

- **Perimeter.** Asset-sale scope varies: MAR R6 "Dispositions" 93M (hotels); CCL R6 "Proceeds from sales of ships" 334M; "proceeds from sale of assets" (36 companies) is broader.
- **Decision.** Excluded (capex is gross).
- **Evidence.** PGR 80M.

### ProceedsFromIssuanceOfCommonStock (494 companies)

- **Meaning.** "Cash inflow from the additional capital contribution".
- **Usage.**
  - REIT ATM offerings are large (O 2,364,144K).
  - 27 companies use it for option exercises or ESPP (PODD peers, TKR, GMED).
  - TRMB nets withholding and is negative (section 1).
- **Decision.** Excluded.
- **Evidence.** DUK 16M; MAR 53M; CCL 3,249M.

## 3. Disagreements with the library

Libraries read: the Mac library `origin/work/tag-library/ranks-1-50` at aea0cf4 (`data-team/47-fsn-store/company_tag_map/ranks_1_50.csv`), and the cloud decisions `origin/work/ritwik-cloud/tag-decisions-2026-11-11` at 83bc4988 (`data-team/tags/decisions/`).

**D1. Buybacks.** The Mac library maps PaymentsForRepurchaseOfCommonStock to `share_buybacks_resolved` for all 47 top-50 companies with no label check. LRCX's mapped evidence label is "Treasury stock purchases, including excise tax payments". FILING-CHECKED: 0000707549-25-000014 R6 line 17, (1,694,723)K, 6M to 2024-12-29.
- Doc 02 2026-11-04 item 4 excludes excise tax, so the LRCX cell should be `combined` (no split printed).
- Population: 33 companies have excise wording and 55 have tax-withholding wording on this tag.
- The cloud branch handles the same perimeter on custom tags (PGR, IBM, AXP) but has no rule for the standard tag. Proposed rule: a label check on the standard tag (excise or withholding wording -> combined or exclude).

**D2. XOM D&A.** The Mac library maps XOM DepreciationDepletionAndAmortization (CF and IS) to `depreciation_and_amortization_resolved`. FILING-CHECKED: XOM 0000034088-26-000045 R7 prints "Depreciation and depletion (includes impairments)" 25,993M.
- By the cloud's own ACN and ISRG rule (D&A combined with other items -> combined), XOM should be `combined`. The same applies to HPQ ("and impairment", R6), DUK ("accretion ... nuclear fuel", R8) and 29 more companies (CSV).
- Not yet decided: whether impairment inside D&A is acceptable for EBITDA. That is a definition call for the Standardization Lead or Dhairya, not a mapping.

**D3. D&A taken from the IS.** The Mac library also maps DDA IS rows (XOM, CVX, LIN) to the same concept. IS and CF D&A can differ (AEO, INDEX row). The rule should take the CF line when both exist. This is a risk, not a proven wrong value: CVX and LIN were not opened.

**D4. Reason class for UN rows.** The Mac library excludes UN rows (ANET, PG) as `cover_or_parenthetical`. Agreed on the exclusion; the reason is wrong.
- At utilities and dual registrants, UN rows are co-registrant cash-flow statements with real subsidiary values (DUK R14, Duke Energy Carolinas).
- The reason should be `coregistrant_statement`, so nobody later "recovers" them as missing parent values.

**D5. Interest and taxes paid.** InterestPaidNet and IncomeTaxesPaidNet have a blank decision (residue) in the Mac library. Not a conflict, but a gap. Proposed: `excluded`, no catalogue concept; bank interest paid (JPM 96,436M) is deposit interest and must not feed any coverage or cash-interest metric.

**D6. Cloud rule 7 and MCD.** No disagreement. AAPL, DUK, XOM, MAR and EWBC all print capex on PaymentsToAcquirePropertyPlantAndEquipment. AMD (inbox 2026-10-26) shows PaymentsForProceedsFromProductiveAssets as a sibling line, consistent with the MCD rule.

**D7. Cloud capex rulings (NEE nuclear fuel, WELL improvements plus CIP, VZ software).** Consistent with this card. The REIT pattern is the same at O (CapitalImprovements) and BXP (OtherProductiveAssets "construction in progress"). Neither is a Mac top-50 company, so I could not check whether the library covers them.

**Agreements.** The Mac library excludes DeferredIncomeTaxExpenseBenefit, the other-investing and other-financing lines, the business-acquisition line, the debt proceeds and repayments lines, the FX effect and the cash change. The cloud branch excludes withholding (IBM). Both match this card.

## 4. Untested scope

- No filing was opened for these: bank capex at more than one bank; utility inventory wording; the FIVE FY2016-2019 split of buybacks from withholding; the 92 widened business-acquisition labels; insurer CFO.
- Calc-parent counts cover two sampled 10-Ks per company, not every filing.
- The FSN store's 2015-2016 coverage (about 517 companies) limits era statements before 2018.
