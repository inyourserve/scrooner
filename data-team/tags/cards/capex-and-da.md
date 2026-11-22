# Card family: capital expenditures and depreciation & amortization (written 2026-11-09 by the Tag Expert; first version from relays)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Tags: `us-gaap:PaymentsToAcquirePropertyPlantAndEquipment`, `PaymentsToAcquireProductiveAssets`, `PaymentsForProceedsFromProductiveAssets`, `PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets`, `PaymentsToDevelopSoftware`, `PaymentsForSoftware`, `PaymentsToAcquireSoftware`; `DepreciationDepletionAndAmortization`, `DepreciationAndAmortization`, `Depreciation`, `AdjustmentForAmortization`, `AmortizationOfIntangibleAssets`, `OtherDepreciationAndAmortization`, `CapitalizedComputerSoftwareAmortization`, `DepreciationAmortizationAndAccretionNet`.
FSN rules: capex `cf.capex_block_member@1-4` (calc position) + `cf.capex_nature_*`; D&A `cf.da_operating_member@1` (calc position) + `cf.da_is_anchor@1-2`. Both are HELD families (release 1 NO for capex; D&A YES 15/15), per data-team/47-fsn-store/concept_rules/cf.jsonl. All rows below: FILING-CHECKED by the named role, not re-opened by me, unless marked.

## 1. Capex
- **Understatement**: PaymentsToAcquirePPE understates capex by ≥10% at about 152 FY2025 10-K filers (Air Lease flight equipment) (Tag Expert R2 run).
- `PaymentsToAcquireProductiveAssets` is Aptiv's "Capital expenditures" (489, 9M 2025, 0001521332-25-000051 R6); by FASB calc it can include software and intangibles. The old concept_mapping had it at p2 provisional (Tag Mapper live read), not unmapped.
- Capitalized software on unmapped tags: `PaymentsToDevelopSoftware` (ArcBest 9,958K), `PaymentsForSoftware` (Skillz, SoundHound; DATA-INFERRED).
- **Discontinued block**: AMD FY2025's (38) on `PaymentsForProceedsFromProductiveAssets` sits in the DISCONTINUED-operations investing block (divestiture 1,356 − 38 = 1,318), not beside continuing PP&E (Data Chief, correcting a Standardization Lead line; 0000002488-26-000018 R8). The calc-position rule must stay inside the continuing investing block.

## 2. D&A
- **FASB 2025 calc**: DDA = Depreciation + Depletion + AdjustmentForAmortization + OtherDepreciationAndAmortization; AdjustmentForAmortization includes financing-cost/discount, DAC, MSR and finance-lease ROU amortization (Gilead R8). So DDA can include non-operating amortization.
- **`DepreciationAndAmortization` is often an IS SUB-line**: Kura IS G&A-level 448K vs CF DDA 14,046K; SBUX IS 1,684.7M vs CF DDA 1,771.5M; Comtech uses it for PP&E-only D&A on the CF (Data Verifier). The old "max of the two tags" fallback picked the larger (Data Chief, code read).
- **Perimeter by filer**: AMD's main line "Depreciation and amortization" (556, 9M 2025) is `OtherDepreciationAndAmortization`, with intangible amortization 1,697 separate. AMD FY2025 `AdjustmentForAmortization` 2,254 = acquisition-intangible amortization in COGS 1,031 + opex 1,223, so it counts in D&A (total 3,004) (Data Chief). ArcBest tags a "Depreciation and amortization" row with `Depreciation`, intangibles separate. TXN prints `CapitalizedComputerSoftwareAmortization` 81M beside Depreciation 1,918M. BRO prints D&A as two IS lines (312M + 55M) with no total. **HD from FY2025**: DDA EXCLUDES intangible amortization (separate `AmortizationOfIntangibleAssets`); before FY2025 it was the single total (0000354950-25-000165 R7 vs -24-000152 R7). MSFT, GOOG, ABT, AMD, INTC, SWKS, SPGI file D&A only as Depreciation + AmortizationOfIntangibleAssets (DATA-INFERRED).
- **Never D&A**: MA "Amortization of customer incentives" 1,830 beside D&A 897 (contract-cost amortization, 0001141391-25-000011 R8). MSFT's only CF D&A line is custom `msft:DepreciationAmortizationAndOther` ("Depreciation, amortization, and other") in every filing 2014-2026: combined, so a reason (`line_presented_combined_with_others`), never a value. KeyCorp `DepreciationAmortizationAndAccretionNet` "…, net" is held once it nets below intangible amortization (Data Engineer, DATA-INFERRED).
- Combined D&A tags understate at about 162 FY2025 filers (AEO: IS vs CF differ) (R2 run).

## 3. Verdicts
- Capex: the calc-position rule inside the continuing investing block, plus nature tags; never a single tag.
- D&A: D&A by composition (the CF operating block's D&A members, per AC-6), with a perimeter label; `DepreciationAndAmortization` alone is never total D&A.

## 4. Folded in from the FSN-expert per-tag cards (2026-11-10)
- `PaymentsToAcquirePropertyPlantAndEquipment`: on the CF face for 94 top-100 names (4,074 lines); labels "Capital expenditures" 812, "Purchases of property and equipment" 705, "Additions to property, plant and equipment" 366. Stored positive, printed in parentheses. MSFT's only capex line in all 54 filings ("Additions to property and equipment": FY2026 115,948M, FY2025 64,551M; Q2 FY2026 10-Q 0001193125-26-027207 R6 prints 29,876 for the quarter, FILING-CHECKED by them). Not total capex where other capex lines exist (Air Lease, §1).
- MSFT `msft:DepreciationAmortizationAndOther` was RECAST in the FY2026 filings: FY2025 34,153M → 29,433M (the difference moved to `msft:GainLossOnInvestmentsAndDerivativeInstruments`) (10-K 0001193125-26-323660; FILING-CHECKED by them). It confirms it is combined, never D&A.

## 5. Release-prep relay 2026-11-11
- Capex in the store = the ported lane detector: one member line per filing or the filing is held (store gate 23/23 Verifier); held multi-line filings = 851 keys at 20 of 98 companies (load run 42966229392). MSFT capex = PaymentsToAcquirePropertyPlantAndEquipment all periods; HD = PaymentsToAcquireProductiveAssets.
- **Founder perimeter 2026-11-04**: capex INCLUDES capitalised software (KEY "Purchases of premises, equipment, and software", FILING-CHECKED), leased fleets, the discontinued block, turnarounds, TI and CIP; EXCLUDES O&G property and acreage acquisitions. Verifier leaks: DVN "Acquisitions of property and equipment" 35M, DOW "Investment in gas field developments" 203M; understatement: AEE FY2021 "Wind generation expenditures" 525M omitted. Multi-line capex (NEE by segment) = sum of the investing-block capex lines.
- D&A: HD held in every filing (one CF D&A line before FY2025, but the IS prints a different D&A total; FY2025+ two lines); JPM D&A = `DepreciationAmortizationAndAccretionNet` (Q1 2014 recast 1,077 → 1,208, latest print wins, Verifier); is_anchor class: utilities (DUK PNW XEL AEE EXC) and VNO serve the IS D&A where the CF line includes nuclear fuel or financing-cost amortization (Verifier). MSFT "Depreciation, amortization, and other" is now a combined row served as `line_presented_combined_with_others` (work/fsn/da-combined-reason 5660394).

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.

## 6. Ritwik (cloud) card notes 7, 13, 14, 24-26 (DATA-INFERRED) and DUK (store read)
- `PaymentsToAcquireProductiveAssets` is not capex when a PP&E purchases line sits on the same CF (MCD 2013-19 "purchases of restaurant businesses").
- NEE capex = FPL + "Capital expenditures" + other + nuclear fuel (0000753308-26-000015 CF l28, 29, 32, 31); "Independent power and other investments" l30 is combined. WELL = capital improvements + CIP (0000766704-26-000010 l23-24). REIT capex = development + TI/leasing commissions + property improvements (PLD 0001193125-26-051453 l27, 30, 31); rental fleet = rental + non-rental equipment (URI). Acquisitions, capitalised interest and proceeds excluded.
- D&A sums: BKNG `DepreciationNonproduction` + `AmortizationOfIntangibleAssets` (0001075531-19-000009 l4-5); SCHW custom + amortization (0000316709-26-000009 l5-6). DUK: serve IS D&A 6,324M; CF 7,704M is combined (accretion + nuclear fuel).
- Combined: "depreciation, amortization and impairment" (GM); "…and other operating gains" (CMCSA); "capital expenditures and investments" (PSX, COP); "capital expenditures, net" (SPG, TDG, CI).

## 7. D&A source rule (Dhairya 2026-11-11, refining the Verifier utility ruling)
- The CF D&A line wins over the IS line UNLESS the CF line is combined (accretion, nuclear fuel, impairment, financing-cost amortization); then the pure IS D&A line is served (DUK FY2025: CF 7,704M combined, IS 6,324M served).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 17 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `AmortizationOfIntangibleAssets`
- **Meaning:** Intangible Asset, Finite-Lived, Amortization Expense (us-gaap, duration, debit). Amount of amortization expense for finite-lived intangible asset. Excludes goodwill and capitalized cost for software to be sold, leased, or marketed.
- **Data point definition:** amortization_of_intangibles: Amortization of acquired finite-lived intangible assets for the period (face line, cash-flow line or note).; depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers). (+1 more)
- **Data point:** amortization_of_intangibles; depreciation_and_amortization; operating_expenses; polarity amortization_of_intangibles:positive; depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#1; depreciation_and_amortization:primary-part#2; depreciation_and_amortization:primary-part#3; depreciation_and_amortization:primary-part#8 (+1 more)
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50; I51; I52; I53; I54; family resolve_all.NARROW[amortization_of_intangibles]
- **Evidence:** 92 companies, 1180 served, 2150 proven, 91 certified cells; last verified 2026-11-15
- **Known problems:** FSN dropped fact 0001413329-23-000025 (fsn_dropped_facts.csv); FSN dropped fact 0001413329-24-000013 (fsn_dropped_facts.csv); pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. ISRG amortization_of_intangibles 2025-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (1)
- **Deprecation:** replaces AmortizationOfAcquiredIntangibleAssets@2013; AmortizationOfIntangiblesNonproductionMember@2013; FiniteLivedIntangibleAssetsAmortizationExpense@2012

### `PaymentsToAcquirePropertyPlantAndEquipment`
- **Meaning:** Payments to Acquire Property, Plant, and Equipment (us-gaap, duration, credit). The cash outflow associated with the acquisition of long-lived, physical assets that are used in the normal conduct of business to produce goods and services and not intended for resale; includes cash outflows to pay for construction of sel...
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive; role capex:primary#1
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX; resolve_all.NARROW[capex]
- **Evidence:** 82 companies, 914 served, 17784 proven, 99 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `DepreciationDepletionAndAmortization`
- **Meaning:** Depreciation, Depletion and Amortization (us-gaap, duration, debit). The aggregate expense recognized in the current period that allocates the cost of tangible assets, intangible assets, or depleting assets to periods that benefit from use of the assets.
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** depreciation_and_amortization; operating_expenses; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#1; depreciation_and_amortization:primary#4
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50; family resolve_all.NARROW[depreciation_and_amortization]
- **Evidence:** 62 companies, 660 served, 10498 proven, 49 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 12 open hit(s) at 1 companies, e.g. CSCO depreciation_and_amortization 2015-07-25 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (12)

### `DepreciationAndAmortization`
- **Meaning:** Depreciation, Depletion and Amortization, Nonproduction (us-gaap, duration, debit). The current period expense charged against earnings on long-lived, physical assets not used in production, and which are not intended for resale, to allocate or recognize the cost of such assets over their useful lives; or to record the red...
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** depreciation_and_amortization; operating_expenses; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#2; depreciation_and_amortization:primary#5
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50; family resolve_all.NARROW[depreciation_and_amortization]
- **Evidence:** 33 companies, 302 served, 3579 proven, 9 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `Depreciation`
- **Meaning:** Depreciation (us-gaap, duration, debit). The amount of expense recognized in the current period that reflects the allocation of the cost of tangible assets over the assets' useful lives. Includes production and non-production related depreciation.
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** depreciation_and_amortization; operating_expenses; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#7; depreciation_and_amortization:primary-part#8; depreciation_and_amortization:primary#10
- **Rules:** X86; I44; I49; I43; I45; I46; I47; I48; I50; resolver functions resolve_da; apply_label_beyond
- **Evidence:** 22 companies, 243 served, 449 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 1 companies, e.g. GOOG depreciation_and_amortization 2021-12-31 (export) (pattern_hits.csv); pattern P06 own_10k_year_hidden: 26 open hit(s) at 3 companies, e.g. ACN depreciation_and_amortization 2020-08-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (26); P05 (2)

### `PaymentsToAcquireProductiveAssets`
- **Meaning:** Payments to Acquire Productive Assets (us-gaap, duration, credit). The cash outflow for purchases of and capital improvements on property, plant and equipment (capital expenditures), software, and other intangible assets.
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive; role capex:primary#2
- **Rules:** K40; K03; K04; K05; K06; K07; K08; K09; family resolve_cf.CAPEX
- **Evidence:** 26 companies, 207 served, 3309 proven, 7 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `DepreciationAmortizationAndAccretionNet`
- **Meaning:** Depreciation, Amortization and Accretion, Net (us-gaap, duration, debit). The aggregate net amount of depreciation, amortization, and accretion recognized during an accounting period. As a noncash item, the net amount is added back to net income when calculating cash provided by or used in operations using the in...
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** depreciation_and_amortization; operating_expenses; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:combined#1
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50
- **Evidence:** 13 companies, 104 served, 943 proven, 20 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `AdjustmentForAmortization`
- **Meaning:** Amortization (us-gaap, duration, debit). The aggregate amount of recurring noncash expense charged against earnings in the period to allocate the cost of assets over their estimated remaining economic lives.
- **Data point definition:** amortization_of_intangibles: Amortization of acquired finite-lived intangible assets for the period (face line, cash-flow line or note).; depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).
- **Data point:** depreciation_and_amortization; amortization_of_intangibles; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#7; depreciation_and_amortization:primary-part#9
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50
- **Evidence:** 8 companies, 100 served, 137 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `PaymentsToAcquireSoftware`
- **Meaning:** Payments to Acquire Software (us-gaap, duration, credit). The cash outflow associated with the acquisition from vendors of software programs or applications for internal use (that is, not to be sold, leased or otherwise marketed to others) that qualify for capitalization.
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX
- **Evidence:** 3 companies, 26 served, 0 proven, 0 certified cells; last verified 2026-11-02
- **Known problems:** none recorded
- **Pattern hits:** none

### `PaymentsForProceedsFromProductiveAssets`
- **Meaning:** Payments for (Proceeds from) Productive Assets (us-gaap, duration, credit). The net cash outflow or inflow from purchases, sales and disposals of property, plant and equipment and other productive assets, including intangibles.
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX
- **Evidence:** 4 companies, 21 served, 61 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `OtherDepreciationAndAmortization`
- **Meaning:** Other Depreciation and Amortization (us-gaap, duration, debit). Amount of expense charged against earnings to allocate the cost of tangible and intangible assets over their remaining economic lives, classified as other.
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).
- **Data point:** depreciation_and_amortization; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#9; depreciation_and_amortization:primary#11
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50
- **Evidence:** 3 companies, 15 served, 56 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. ACN depreciation_and_amortization 2026-08-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (1)

### `PaymentsToDevelopSoftware`
- **Meaning:** Payments to Develop Software (us-gaap, duration, credit). The cash outflow associated with the development or modification of software programs or applications for internal use (that is, not to be sold, leased or otherwise marketed to others) that qualify for capitalization.
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX
- **Evidence:** 1 companies, 9 served, 0 proven, 0 certified cells; last verified 2026-11-02
- **Known problems:** none recorded
- **Pattern hits:** none

### `PaymentsForSoftware`
- **Meaning:** Payments for Software (us-gaap, duration, credit). The cash outflow associated with the development, modification or acquisition of software programs or applications for internal use (that is, not to be sold, leased or otherwise marketed to others) that qualify for capitalization.
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX
- **Evidence:** 1 companies, 6 served, 0 proven, 0 certified cells; last verified 2026-11-02
- **Known problems:** none recorded
- **Pattern hits:** none

### `DepreciationNonproduction`
- **Meaning:** Depreciation, Nonproduction (us-gaap, duration, debit). The expense recognized in the current period that allocates the cost of nonproduction tangible assets over their useful lives.
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).
- **Data point:** depreciation_and_amortization
- **Rules:** none
- **Evidence:** 1 companies, 5 served, 0 proven, 0 certified cells; last verified 2026-11-02
- **Known problems:** none recorded
- **Pattern hits:** none

### `Capital`
- **Meaning:** Banking Regulation, Total Capital, Actual (us-gaap, instant, credit). Amount of total capital as defined by regulatory framework.
- **Data point:** none (the resolver never serves it)
- **Rules:** C02; B29; resolver functions resolve; shares
- **Evidence:** 0 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none

### `DepreciationAmortizationAndOther`
- **Meaning:** (no taxonomy label) (custom)
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).
- **Data point:** depreciation_and_amortization; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:primary#6
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50
- **Evidence:** 3 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none

### `PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets`
- **Meaning:** (no taxonomy label) (unknown)
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive
- **Rules:** K40; K03; K04; K05; K06; K07; K08; K09; family resolve_cf.CAPEX
- **Evidence:** 0 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
